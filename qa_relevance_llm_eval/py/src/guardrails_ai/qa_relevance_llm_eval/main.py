from typing import Any, Callable, Dict, Optional

from guardrails_ai.response_evaluator import ResponseEvaluator
from guardrails.validator_base import (
    ValidationResult,
    register_validator,
)


@register_validator(name="guardrails/qa_relevance_llm_eval", data_type="string")
class QARelevanceLLMEval(ResponseEvaluator):  # type: ignore
    """Validates that an answer is relevant to the given prompt.

    This validator prompts the LLM to self-evaluate
    the relevance of the response to the given prompt.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/qa_relevance_llm_eval`  |
    | Supported data types          | `string`                            |
    | Programmatic fix              | None                                |

    Args:
        llm_callable (str, optional): Model name to make the litellm call.
            Defaults to `gpt-3.5-turbo`
        on_fail (Callable, optional): A function to call when validation fails.
            Defaults to None.
    """  # noqa

    def __init__(
        self,
        llm_callable: Optional[str] = "gpt-3.5-turbo",
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail, llm_callable=llm_callable)

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates that the LLM response is relevant to the given prompt."""

        original_prompt = metadata.get("original_prompt", None)
        if original_prompt is None:
            raise RuntimeError(
                """Missing 'original_prompt' in metadata.
                Please provide the prompt, and try again.
                """
            )

        metadata[
            "validation_question"
        ] = f"""Is the above 'Response' relevant to the following 'Prompt'?
        Prompt:
        {original_prompt}
        """

        return super().validate(value, metadata)
