import json
import os
from typing import Any, Callable, Dict, List, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from guardrails.stores.context import get_call_kwarg
from litellm import completion, get_llm_provider


@register_validator(name="guardrails/saliency_check", data_type="string")
class SaliencyCheck(Validator):
    """Checks that the summary covers the list of topics present in the
    document.

    The validator uses an LLM to extract topics from the document and the summary.
    It then computes the overlap between the topics in the document and the summary.
    If the overlap is less than a threshold, the validation fails.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/saliency_check`         |
    | Supported data types          | `string`                            |
    | Programmatic fix              | None                                |

    Args:

        docs_dir: Path to the directory containing the documents.
        llm_callable: Name of the LLM to use for extracting topics from the document.
            Default is `gpt-3.5-turbo` for LiteLLM.
        threshold: Minimum threshold for overlap between topics in document and summary.
            If the overlap is less than the threshold, the validation fails. Default is 0.25.
    """  # noqa

    def __init__(
        self,
        docs_dir: str,
        llm_callable: str = "gpt-3.5-turbo",  # str for litellm model name
        threshold: float = 0.25,
        on_fail: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(
            on_fail,
            docs_dir=docs_dir,
            llm_callable=llm_callable,
            threshold=threshold,
            **kwargs,
        )

        self.llm_callable = llm_callable
        self._threshold = threshold

        # Load documents
        self._document_store = {}
        for doc_path in os.listdir(docs_dir):
            with open(os.path.join(docs_dir, doc_path)) as f:
                text = f.read()

            # Precompute topics for each document
            self._document_store[doc_path] = self._get_topics(text)

    @property
    def _topics(self) -> List[str]:
        """Return a list of topics that can be used in the validator."""
        # Merge topics from all documents
        topics = set()
        for doc_topics in self._document_store.values():
            topics.update(doc_topics)
        return list(topics)

    def get_evaluation_prompt(
        self, text: str, topics: Optional[List[str]] = None
    ) -> str:
        """Generates the prompt to send to the LLM.

        Args:
            text (str): The text to send to the LLM.
            topics (Optional[List[str]]): The initial seed topics to send to the LLM.

        Returns:
            prompt (str): The prompt to send to the LLM.
        """
        topics_seed = ""
        if topics:
            topics_seed = f"""
            Here's a seed list of topics, select topics from this list if they are covered in the doc:

            {", ".join(topics)}
            """

        prompt = f"""
        Extract a list of topics from the following text:

        {text}

        {topics_seed}

        Return the output as a JSON with a single key "topics" containing a list of topics. 
        Any additional text is strictly prohibited. Make sure that the topics are relevant to text, 
        and the topics are not too specific or general.
        """
        return prompt

    def get_llm_response(self, prompt: str) -> str:
        """Gets the response from the LLM.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            str: The response from the LLM.
        """
        # 0. Create messages
        messages = [{"content": prompt, "role": "user"}]

        # 0b. Setup auth kwargs if the model is from OpenAI
        kwargs = {}
        _model, provider, *_rest = get_llm_provider(self.llm_callable)
        print("self.llm_callable: ", self.llm_callable)
        print("provider: ", provider)
        if provider == "openai":
            kwargs["api_key"] = get_call_kwarg("api_key") or os.environ.get(
                "OPENAI_API_KEY"
            )
            print("kwargs: ", kwargs)

        # 1. Get LLM response
        # Strip whitespace and convert to lowercase
        try:
            response = completion(model=self.llm_callable, messages=messages, **kwargs)
            response = response.choices[0].message.content or ""  # type: ignore
            response = response.strip().lower()
        except Exception as e:
            raise RuntimeError(f"Error getting response from the LLM: {e}") from e

        # 3. Return the response
        return response

    def _get_topics(self, text: str, topics: Optional[List[str]] = None) -> List[str]:
        """Extract topics from a string."""
        prompt = self.get_evaluation_prompt(text, topics)
        response = self.get_llm_response(prompt)

        try:
            response = json.loads(response)
            topics = response.get("topics", [])
        except Exception as e:
            raise RuntimeError(f"Error parsing response from the LLM: {e}") from e

        print(f"Extracted topics:\n{topics}")
        return topics or []

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validation method for the SaliencyCheck validator."""
        print("Extracting topics from the summary...")
        topics_in_summary = self._get_topics(value, topics=self._topics)

        # Compute overlap between topics in document and summary
        intersection = set(topics_in_summary).intersection(set(self._topics))
        overlap = len(intersection) / len(self._topics)

        print(f"Overlap: {overlap}")

        if overlap < self._threshold:
            return FailResult(
                error_message=(
                    f"The summary \nSummary: {value}\n does not cover these topics:\n"
                    f"{set(self._topics).difference(intersection)}"
                ),
                fix_value="",
            )

        return PassResult()
