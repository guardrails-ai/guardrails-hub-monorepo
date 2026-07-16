import itertools
import warnings
import nltk
import numpy as np
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple

from guardrails.utils.docs_utils import get_chunks_from_text
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from sentence_transformers import SentenceTransformer


@register_validator(name="guardrails/provenance_embeddings", data_type="string")
class ProvenanceEmbeddings(Validator):
    """Validates that LLM-generated text matches some source text based on
    distance in embedding space.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/provenance_embeddings`  |
    | Supported data types          | `string`                            |
    | Programmatic fix              | None                                |

    Args:
        threshold: The minimum cosine distance between the generated text and
            the source text. Defaults to 0.8. Lower the threshold, the more
            number of dissimilar sentences will be flagged.
        validation_method: Whether to validate at the sentence level OR full text.
            Must be one of `sentence` or `full`. Defaults to `sentence`

    Other parameters: Metadata
        query_function (Callable, optional): A callable that takes a string and returns
            a list of (chunk, score) tuples.
        sources (List[str], optional): The source text.
        embed_function (Callable, optional): A callable that creates embeddings for the sources.
            Must accept a list of strings and return an np.array of floats.

    In order to use this validator, you must provide either a `query_function` or
    `sources` with an `embed_function` in the metadata.

    If providing query_function, it should take a string as input and return a list of
    (chunk, score) tuples. The chunk is a string and the score is a float representing
    the cosine distance between the chunk and the input string. The list should be
    sorted in ascending order by score.

    Note: The score should represent distance in embedding space, not similarity. i.e.,
    lower is better and the score should be 0 if the chunk is identical to the input
    string.

    Example:
        ```py
        def query_function(text: str, k: int) -> List[Tuple[str, float]]:
            return [("This is a chunk", 0.9), ("This is another chunk", 0.8)]

        guard = Guard.for_rail(...)
        guard(
            openai.ChatCompletion.create(...),
            prompt_params={...},
            temperature=0.0,
            metadata={"query_function": query_function},
        )
        ```


    If providing sources, it should be a list of strings. The embed_function should
    take a string or a list of strings as input and return a np array of floats.
    The vector should be normalized to unit length.

    Example:
        ```py
        def embed_function(text: Union[str, List[str]]) -> np.ndarray:
            return np.array([[0.1, 0.2, 0.3]])

        guard = Guard.for_rail(...)
        guard(
            openai.ChatCompletion.create(...),
            prompt_params={...},
            temperature=0.0,
            metadata={
                "sources": ["This is a source text"],
                "embed_function": embed_function
            },
        )
        ```
    """  # noqa

    def __init__(
        self,
        threshold: float = 0.8,
        validation_method: str = "sentence",
        on_fail: Optional[Callable] = None,
        load_nltk_data: bool = True,
        **kwargs,
    ):
        if load_nltk_data:
            from .post_install import load_nltk_data as _load_nltk_data

            _load_nltk_data()
        super().__init__(
            on_fail, threshold=threshold, validation_method=validation_method, **kwargs
        )
        self._threshold = float(threshold)
        if validation_method not in ["sentence", "full"]:
            raise ValueError("validation_method must be 'sentence' or 'full'.")
        self._validation_method = validation_method
        self._default_model = None

    def get_query_function(self, metadata: Dict[str, Any]) -> Callable:
        """Get the query function from metadata.

        If `query_function` is provided, it will be used. Otherwise, `sources` and
        `embed_function` will be used to create a default query function.
        """
        query_fn = metadata.get("query_function", None)
        sources = metadata.get("sources", None)

        # Check that query_fn or sources are provided
        if query_fn is not None:
            if sources is not None:
                warnings.warn(
                    "Both `query_function` and `sources` are provided in metadata. "
                    "`query_function` will be used."
                )
            return query_fn

        if sources is None:
            raise ValueError(
                "You must provide either `query_function` or `sources` in metadata."
            )

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
            if not self._default_model:
                self._default_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
            MODEL = self._default_model

            # Create embed function
            def st_embed_function(sources: list[str]):
                return MODEL.encode(sources)

            embed_function = st_embed_function
        return partial(
            self.query_vector_collection,
            sources=metadata["sources"],
            chunk_strategy=chunk_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            distance_metric=distance_metric,
            embed_function=embed_function,
        )

    def validate_each_sentence(
        self, value: Any, query_function: Callable, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate each sentence in the response."""

        # Split the value into sentences using nltk sentence tokenizer.
        sentences = nltk.sent_tokenize(value)

        unsupported_sentences = []
        supported_sentences = []
        for sentence in sentences:
            most_similar_chunks = query_function(text=sentence, k=1)
            if most_similar_chunks is None:
                unsupported_sentences.append(sentence)
                continue
            most_similar_chunk = most_similar_chunks[0]
            if most_similar_chunk[1] < self._threshold:
                supported_sentences.append((sentence, most_similar_chunk[0]))
            else:
                unsupported_sentences.append(sentence)

        metadata["unsupported_sentences"] = "- " + "\n- ".join(unsupported_sentences)
        metadata["supported_sentences"] = supported_sentences
        if unsupported_sentences:
            unsupported_sentences = "- " + "\n- ".join(unsupported_sentences)
            return FailResult(
                metadata=metadata,
                error_message=(
                    f"None of the following sentences in your response are supported "
                    "by provided context:"
                    f"\n{metadata['unsupported_sentences']}"
                ),
                fix_value="\n".join(s[0] for s in supported_sentences),
            )
        return PassResult(metadata=metadata)

    def validate_full_text(
        self, value: Any, query_function: Callable, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate the full text in the response."""
        most_similar_chunks = query_function(text=value, k=1)
        if most_similar_chunks is None:
            metadata["unsupported_text"] = value
            metadata["supported_text_citations"] = {}
            return FailResult(
                metadata=metadata,
                error_message=(
                    "The following text in your response is not supported by the "
                    "supported by the provided context:\n" + value
                ),
            )
        most_similar_chunk = most_similar_chunks[0]
        if most_similar_chunk[1] > self._threshold:
            metadata["unsupported_text"] = value
            metadata["supported_text_citations"] = {}
            return FailResult(
                metadata=metadata,
                error_message=(
                    "The following text in your response is not supported by the "
                    "supported by the provided context:\n" + value
                ),
            )

        metadata["unsupported_text"] = ""
        metadata["supported_text_citations"] = {
            value: most_similar_chunk[0],
        }
        return PassResult(metadata=metadata)

    def validate(self, value: Any, metadata: Dict[str, Any]) -> ValidationResult:
        """Validation function for the ProvenanceEmbeddings validator."""
        query_function = self.get_query_function(metadata)

        if self._validation_method == "sentence":
            return self.validate_each_sentence(value, query_function, metadata)
        return self.validate_full_text(value, query_function, metadata)

    @staticmethod
    def query_vector_collection(
        text: str,
        k: int,
        sources: List[str],
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
        source_embeddings = np.array(embed_function(chunks)).squeeze()
        query_embedding = embed_function(text).squeeze()

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
            top_similarities = [cos_sim[j] for j in top_indices]
            top_chunks = [chunks[j] for j in top_indices]
        else:
            raise ValueError("distance_metric must be 'cosine'.")

        return list(zip(top_chunks, top_similarities))
