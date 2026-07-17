import os
from functools import partial
import itertools
from typing import Any, Callable, Dict, List, Optional, Tuple
import warnings
import numpy as np
import torch
import nltk
import requests
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from guardrails.utils.docs_utils import get_chunks_from_text
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from sentence_transformers import SentenceTransformer


@register_validator(name="guardrails/provenance_nli", data_type="string")
class ProvenanceNLI(Validator):
    """Detects and removes hallucinations from LLM-generated text using an NLI model.

    This validator uses a fine-tuned version of an NLI model
    (provided by the user with 'checkpoint').

    **Key Properties**

    | Property                      | Description                        |
    | ----------------------------- | ---------------------------------  |
    | Name for `format` attribute   | `guardrails/provenance_nli` |
    | Supported data types          | `string`                           |
    | Programmatic fix              | None                               |

    Args:
        inference_endpoint (str): URL for hosted inference endpoint. Required for hosted models only.
        model_name (str): Name of the model to be used. Required for local models only.
        model_checkpoint_path (str): Local path of finetuned model. Required for local models only.
        top_k (int): The number of chunks to return from the query function. Defaults to 1.
        min_confidence (float): The minumum confidence score required to pass validation. Defaults to 0.3.
        max_length (int): Maximum length (in tokens) to use for padding or truncation. Defaults to 256. Required for local models only.
    """

    def __init__(
        self,
        inference_endpoint: Optional[str] = None,
        model_name: Optional[str] = None,
        model_checkpoint_path: Optional[str] = None,
        top_k: Optional[int] = 1,
        max_length: Optional[int] = 256,
        min_confidence: Optional[float] = 0.3,
        on_fail: Optional[Callable] = None,
        load_nltk_data: bool = True,
    ):
        if load_nltk_data:
            from .post_install import load_nltk_data as _load_nltk_data

            _load_nltk_data()
        super().__init__(
            on_fail,
            validation_method="sentence",
            top_k=top_k,
            model_name=model_name,
            model_checkpoint_path=model_checkpoint_path,
            max_length=max_length,
        )
        self._inference_endpoint = inference_endpoint
        self._model_name = model_name
        self._model_checkpoint_path = model_checkpoint_path
        self._top_k = top_k
        self._max_length = max_length
        self._min_confidence = min_confidence

        self._label_names = ["entailment", "not_entailment"]

        self._tokenizer = None
        self._model = None
        self._device = None

        if model_name:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self._model_name, return_tensors="pt"
            )
            self._model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self._device = "cuda" if torch.cuda.is_available() else "cpu"

            if model_checkpoint_path:
                _map_location = (
                    torch.device("cpu") if not torch.cuda.is_available() else None
                )
                if isinstance(model_checkpoint_path, str):
                    self._model.load_state_dict(
                        torch.load(model_checkpoint_path, map_location=_map_location)
                    )
                else:
                    raise ValueError("model_checkpoint_path must be a string")

            self._model.to(self._device)

        if not inference_endpoint and not model_name:
            raise ValueError(
                "You must provide either `inference_endpoint` or `model_name`!"
            )

    def validate(self, value: Any, metadata: Dict[str, Any] = {}) -> ValidationResult:
        query_function = self.get_query_function(metadata)
        if query_function is None:
            raise ValueError("Query function is not provided or is None.")
        return self.validate_each_sentence(value, query_function, metadata)

    def get_query_function(self, metadata: Dict[str, Any]) -> Callable | None:
        query_fn = metadata.get("query_function", None)
        sources = metadata.get("sources", None)

        # Check that query_fn or sources are provided
        if query_fn is not None and sources is not None:
            warnings.warn(
                "Both `query_function` and `sources` are provided in metadata. "
                "`query_function` will be used."
            )
        elif query_fn is None and sources is None:
            raise ValueError(
                "You must provide either `query_function` or `sources` in metadata."
            )
        elif query_fn is None and sources is not None:
            # Check chunking strategy
            chunk_strategy = metadata.get("chunk_strategy", "sentence")
            if chunk_strategy not in ["sentence", "word", "char", "token"]:
                raise ValueError(
                    "`chunk_strategy` must be one of 'sentence', 'word', 'char', "
                    "or 'token'."
                )
            chunk_size = metadata.get("chunk_size", 5)
            chunk_overlap = metadata.get("chunk_overlap", 2)

            # Check distance metric
            distance_metric = metadata.get("distance_metric", "cosine")
            if distance_metric not in ["cosine", "euclidean"]:
                raise ValueError(
                    "`distance_metric` must be one of 'cosine' or 'euclidean'."
                )

            # Check embed model
            embed_function = metadata.get("embed_function", None)
            if embed_function is None:
                # Load model for embedding function
                MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2")

                # Create embed function
                def st_embed_function(sources: list[str]):
                    return MODEL.encode(sources)

                embed_function = st_embed_function
            query_fn = partial(
                self.query_vector_collection,
                sources=metadata["sources"],
                chunk_strategy=chunk_strategy,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                distance_metric=distance_metric,
                embed_function=embed_function,
            )
        return query_fn

    def _get_model_prediction_from_local_model(
        self, premise: str, hypothesis: str
    ) -> Tuple[str, float]:
        """Returns the model prediction for the given premise and
        hypothesis."""
        if self._tokenizer is None:
            raise ValueError("Tokenizer is not initialized.")
        if self._model is None:
            raise ValueError("Model is not initialized.")

        input = self._tokenizer.encode_plus(
            premise,
            hypothesis,
            max_length=self._max_length,
            return_token_type_ids=True,
            truncation=True,
        )

        input_ids = torch.Tensor(input["input_ids"]).long().unsqueeze(0)
        # remember bart doesn't have 'token_type_ids', remove the line below if you are using bart.
        token_type_ids = torch.Tensor(input["token_type_ids"]).long().unsqueeze(0)
        attention_mask = torch.Tensor(input["attention_mask"]).long().unsqueeze(0)

        output = self._model(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            labels=None,
        )
        # Compute softmax predictions and map them to label names
        predictions = dict(
            zip(self._label_names, torch.softmax(output["logits"][0], dim=-1).tolist())
        )

        # Find the max label and its corresponding prediction value
        max_label, max_value = max(predictions.items(), key=lambda x: x[1])

        # If necessary, you can use max_value for further processing or logging
        confidence = round(predictions[max_label], 3)
        return max_label, confidence

    def _get_model_prediction_from_inference_endpoint(
        self, premise: str, hypothesis: str, metadata: Dict[str, Any]
    ) -> Tuple[str, float]:
        hf_token = metadata.get("hf_token", os.environ.get("HF_TOKEN"))

        if self._inference_endpoint is None:
            raise ValueError("Inference endpoint is not initialized.")

        response = requests.post(
            self._inference_endpoint,
            data={"inputs": hypothesis},
            headers={"Authorization": f"Bearer {hf_token}"},
        )

        if not response.ok:
            raise ValueError(
                "Call to inference endpoint failed!", response.raise_for_status()
            )

        prediction = response.json()
        if prediction and len(prediction) > 0:
            max_result = max(prediction[0], key=lambda p: p["score"])
            max_label = max_result.get("label")
            confidence = round(max_result.get("score"), 3)
            return max_label, confidence
        raise ValueError("The inference endpoint returned an invalid response!")

    def get_model_prediction(
        self, premise: str, hypothesis: str, metadata: Dict[str, Any]
    ) -> Tuple[str, float]:
        if self._inference_endpoint:
            return self._get_model_prediction_from_inference_endpoint(
                premise, hypothesis, metadata
            )
        return self._get_model_prediction_from_local_model(premise, hypothesis)

    def get_nli_evaluation(
        self, text: str, query_function: Callable, metadata: Dict[str, Any]
    ) -> bool:
        """Create hypothesis and premise and then return NLI model
        prediction."""

        # Get the relevant chunks using the query function
        relevant_chunks = query_function(text=text, k=self._top_k)

        if not relevant_chunks:
            # Raise warning and return True
            warnings.warn(
                "No relevant chunks were found. Vector collection probably empty. "
                "No NLI evaluation will be performed."
            )
            return False

        hypothesis = text

        for chunk in relevant_chunks:
            # Create the premise and hypothesis
            premise = chunk

            # Get NLI model prediction and confidence value
            nli_prediction, confidence = self.get_model_prediction(
                premise, hypothesis, metadata
            )
            if nli_prediction == "entailment" and confidence > (
                self._min_confidence or 0.5
            ):
                return True

        return False

    def validate_each_sentence(
        self, value: Any, query_function: Callable, metadata: Dict[str, Any]
    ) -> ValidationResult:
        # Split the value into sentences using nltk sentence tokenizer.
        sentences = nltk.sent_tokenize(value)

        unsupported_sentences = []
        supported_sentences = []
        for sentence in sentences:
            eval = self.get_nli_evaluation(sentence, query_function, metadata)
            if not eval:
                unsupported_sentences.append(sentence)
            else:
                supported_sentences.append(sentence)

        if unsupported_sentences:
            unsupported_sentences = "- " + "\n- ".join(unsupported_sentences)
            return FailResult(
                metadata=metadata,
                error_message=(
                    f"The following sentences in your response are not supported "
                    "by the provided context:"
                    f"\n{unsupported_sentences}"
                ),
                fix_value="\n".join(supported_sentences),
            )
        return PassResult(metadata=metadata)

    def query_vector_collection(
        self,
        text: str,
        k: int,
        sources: List[str],
        *,
        embed_function: Callable,
        chunk_strategy: str = "sentence",
        chunk_size: int = 5,
        chunk_overlap: int = 2,
        distance_metric: str = "cosine",
    ) -> List[Tuple[str, float]]:
        chunks = [
            get_chunks_from_text(source, chunk_strategy, chunk_size, chunk_overlap)
            for source in sources
        ]
        chunks = list(itertools.chain.from_iterable(chunks))

        # Create embeddings
        source_embeddings = np.array(embed_function(chunks))
        query_embedding = np.array(embed_function([text]))

        # Ensure both embeddings are 2D
        if source_embeddings.ndim == 1:
            source_embeddings = source_embeddings.reshape(1, -1)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Compute distances
        if distance_metric == "cosine":
            cos_sim = 1 - (
                np.dot(source_embeddings, query_embedding)
                / (
                    np.linalg.norm(source_embeddings, axis=1)
                    * np.linalg.norm(query_embedding)
                )
            )
            top_indices = np.argsort(cos_sim)[:k]
            top_chunks = [chunks[j] for j in top_indices]
        else:
            raise ValueError("distance_metric must be 'cosine'.")

        return top_chunks
