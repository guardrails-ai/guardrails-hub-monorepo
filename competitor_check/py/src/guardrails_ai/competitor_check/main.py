import json
import re
from typing import Any, Callable, Dict, List, Optional

import nltk
import spacy
from guardrails.validator_base import ErrorSpan
from guardrails.validators import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(
    name="guardrails/competitor_check", data_type="string", has_guardrails_endpoint=True
)
class CompetitorCheck(Validator):
    """Validates that LLM-generated text is not naming any competitors from a
    given list.

    In order to use this validator you need to provide an extensive list of the
    competitors you want to avoid naming including all common variations.

    Args:
        competitors (List[str]): List of competitors you want to avoid naming
    """

    def chunking_function(self, chunk: str):
        """
        Use a sentence tokenizer to split the chunk into sentences.

        Because using the tokenizer is expensive, we only use it if there
        is a period present in the chunk.
        """
        # using the sentence tokenizer is expensive
        # we check for a . to avoid wastefully calling the tokenizer
        if "." not in chunk:
            return []
        sentences = nltk.sent_tokenize(chunk)
        if len(sentences) == 0:
            return []
        if len(sentences) == 1:
            sentence = sentences[0].strip()
            # this can still fail if the last chunk ends on the . in an email address
            if sentence[-1] == ".":
                return [sentence, ""]
            else:
                return []

        # return the sentence
        # then the remaining chunks that aren't finished accumulating
        return [sentences[0], "".join(sentences[1:])]

    def __init__(
        self,
        competitors: List[str],
        on_fail: Optional[Callable] = None,
        load_nltk_data: bool = True,
        spacy_model: str = "en_core_web_trf",
        **kwargs,
    ):
        if load_nltk_data:
            from .post_install import load_nltk_data as _load_nltk_data

            _load_nltk_data()
        super().__init__(
            competitors=competitors,
            on_fail=on_fail,
            spacy_model=spacy_model,
            **kwargs,
        )
        if (
            not self.use_local
            and self.validation_endpoint
            and "guardrailsai.com" in self.validation_endpoint
        ):
            import warnings

            warnings.warn(
                "Guardrails-hosted remote inference is deprecated and will be shut "
                "down on 2026-08-06. This validator is configured to use the hosted "
                f"endpoint {self.validation_endpoint}. Pass use_local=True to run the "
                "model locally, or set validation_endpoint to your own hosted "
                "inference server. See "
                "https://www.guardrailsai.com/docs/concepts/remote_validation_inference",
                DeprecationWarning,
                stacklevel=2,
            )

        self._competitors = competitors
        self._spacy_model = spacy_model
        if self.use_local:
            self.nlp = spacy.load(spacy_model)

    def exact_match(self, text: str, competitors: List[str]) -> List[str]:
        """Performs exact match to find competitors from a list in a given
        text.

        Args:
            text (str): The text to search for competitors.
            competitors (list): A list of competitor entities to match.

        Returns:
            list: A list of matched entities.
        """

        found_entities = []
        for entity in competitors:
            pattern = rf"\b{re.escape(entity)}\b"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found_entities.append(entity)
        return found_entities

    def extract_entities_in_competitors_list(
        self, entities: List[str], competitors: List[str]
    ) -> List:
        """Checks if any entity from a list is present in a given list of
        competitors.

        Args:
            entities (list): A list of entities to check
            competitors (list): A list of competitor names to match

        Returns:
            List: List of found competitors
        """

        found_competitors = []
        for entity in entities:
            for item in competitors:
                pattern = rf"\b{re.escape(item)}\b"
                match = re.search(pattern, entity, re.IGNORECASE)
                if match:
                    found_competitors.append(item)
        return found_competitors

    def validate(self, value: str, metadata=Dict) -> ValidationResult:
        """Checks a text to find competitors' names in it.

        While running, store sentences naming competitors and generate a fixed output
        filtering out all flagged sentences.

        Args:
            value (str): The value to be validated.
            metadata (Dict, optional): Additional metadata. Defaults to empty dict.

        Returns:
            ValidationResult: The validation result.
        """

        self.original_sentences = nltk.sent_tokenize(
            value
        )  # Store the original sentences
        competitor_entities = self.find_competitor_matches(self.original_sentences)
        error_spans = self.compute_error_spans(
            self.original_sentences, competitor_entities
        )
        filtered_output = self.compute_filtered_output(
            self.original_sentences, competitor_entities
        )

        list_of_competitors_found = self.flatten_competitors(competitor_entities)

        if len(error_spans) > 0:
            return FailResult(
                error_message=(
                    f"Found the following competitors: {', '.join(list_of_competitors_found)}. "
                    "Please avoid naming those competitors next time"
                ),
                fix_value=filtered_output,
                error_spans=error_spans,
            )
        else:
            return PassResult()

    def _inference_local(self, model_input: Any) -> List[List[str]]:
        """Local inference method to detect and anonymize competitor names."""
        text = model_input["text"]
        competitors = model_input["competitors"]

        if isinstance(text, str):
            text = [text]

        all_located_entities = []
        competitors_lowercase = [comp.lower() for comp in competitors]

        for t in text:
            doc = self.nlp(t)
            located_entities = []
            for ent in doc.ents:
                if ent.text.lower() in competitors_lowercase:
                    located_entities.append(ent.text)
            all_located_entities.append(located_entities)

        return all_located_entities

    def _inference_remote(self, model_input: Any) -> List[List[str]]:
        """Remote inference method for a hosted ML endpoint."""

        text = model_input["text"]
        competitors = model_input["competitors"]

        if isinstance(text, str):
            text = [text]

        request_body = {
            "inputs": [
                {
                    "name": "text",
                    "shape": [len(text)],
                    "data": text,
                    "datatype": "BYTES",
                },
                {
                    "name": "competitors",
                    "shape": [len(competitors)],
                    "data": competitors,
                    "datatype": "BYTES",
                },
            ]
        }
        response = self._hub_inference_request(
            json.dumps(request_body),
            self.validation_endpoint,  # type: ignore
        )

        if not response or "outputs" not in response:
            raise ValueError("Invalid response from remote inference", response)

        ner_entities = []
        for output in response["outputs"]:
            ner_entities.append(output["data"][0])

        return ner_entities

    # retuns a list of competitors found in each sentence
    def find_competitor_matches(self, sentences: List[str]) -> List[List[str]]:
        suspect_entity_sentences = []
        suspect_entity_sentences_indices = []
        for idx, sentence in enumerate(sentences):
            entities = self.exact_match(sentence, self._competitors)
            if entities:
                suspect_entity_sentences.append(sentence)
                suspect_entity_sentences_indices.append(idx)

        ner_located_competitors = self._inference(
            {"text": suspect_entity_sentences, "competitors": self._competitors}
        )

        competitors = []
        for idx, sentence in enumerate(sentences):
            if idx in suspect_entity_sentences_indices:
                ner_entities = ner_located_competitors.pop(0)
                competitors.append(
                    self.extract_entities_in_competitors_list(
                        ner_entities, self._competitors
                    )
                )
            else:
                competitors.append([])

        return competitors

    # returns the compiled value by replacing all competitor mentions with [COMPETITOR]
    def compute_filtered_output(
        self, sentences: List[str], competitors_per_sentence: List[List[str]]
    ) -> str:
        assert len(sentences) == len(competitors_per_sentence)

        filtered_output = ""
        for idx, sentence in enumerate(sentences):
            competitors = competitors_per_sentence[idx]
            filtered_output += self.filter_output_in_sentence(sentence, competitors)

        return filtered_output

    def filter_output_in_sentence(self, sentence: str, competitors: List[str]) -> str:
        if len(competitors) == 0:
            return sentence

        filtered_text = sentence

        for competitor in competitors:
            pattern = re.compile(re.escape(competitor), re.IGNORECASE)
            filtered_text = pattern.sub("[COMPETITOR]", filtered_text)

        return filtered_text

    def compute_error_spans(
        self, sentences: List[str], competitors_per_sentence: List[List[str]]
    ) -> List[ErrorSpan]:
        assert len(sentences) == len(competitors_per_sentence)

        error_spans: List[ErrorSpan] = []
        for idx, sentence in enumerate(sentences):
            competitors = competitors_per_sentence[idx]
            sentence_lower = sentence.lower()

            for competitor in competitors:
                competitor_lower = competitor.lower()
                start_idx = 0
                while sentence_lower.find(competitor_lower, start_idx) > -1:
                    start_idx = sentence_lower.find(competitor_lower, start_idx)
                    end_idx = start_idx + len(competitor_lower)
                    actual_text = sentence[start_idx:end_idx]
                    error_spans.append(
                        ErrorSpan(
                            start=start_idx,
                            end=end_idx,
                            reason=f"Competitor was found: {actual_text}",
                        )
                    )
                    start_idx = end_idx

        return error_spans

    def flatten_competitors(self, competitor_entities: List[List[str]]) -> List[str]:
        list_of_competitors_found = []
        for sentence in self.original_sentences:
            sentence_lower = sentence.lower()
            for competitor in self._competitors:
                if competitor.lower() in sentence_lower:
                    start_idx = sentence_lower.index(competitor.lower())
                    actual_text = sentence[start_idx : start_idx + len(competitor)]
                    list_of_competitors_found.append(actual_text)
        return list(set(list_of_competitors_found))
