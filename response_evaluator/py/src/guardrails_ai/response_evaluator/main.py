import os
from typing import Any, Callable, Dict, Optional
from warnings import warn

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from guardrails.stores.context import get_call_kwarg
from litellm import completion, get_llm_provider


@register_validator(name="guardrails/response_evaluator", data_type="string")
class ResponseEvaluator(Validator):
    """Validates an LLM-generated output by prompting another LLM to evaluate the output.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/response_evaluator`   |
    | Supported data types          | `string`                          |
    | Programmatic fix              | N/A                               |

    Args:
        llm_callable (str, optional): The LiteLLM model name string to use. Defaults to "gpt-3.5-turbo".
        on_fail (Callable, optional): A function to call when validation fails.
            Defaults to None.
    """

    def __init__(
        self,
        llm_callable: str = "gpt-3.5-turbo",  # str for litellm model name
        on_fail: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(on_fail, llm_callable=llm_callable, **kwargs)
        self.llm_callable = llm_callable

    def get_validation_prompt(self, value: str, question: str) -> str:
        """Generates the prompt to send to the LLM.

        Args:
            value (str): The value to validate.
            question (str): The question to ask the LLM.

        Returns:
            prompt (str): The prompt to send to the LLM.
        """
        prompt = f"""
        As an oracle of truth and logic, your task is to evaluate a 'Response' by answering a simple rhetorical 'Question' based on the context of that response.
        You have been provided with the 'Response' and a 'Question', and you need to generate 'Your Answer'.
        Please answer the question with just a 'Yes' or a 'No'. Any other answer is strictly forbidden.
        You'll be evaluated based on how well you understand the question and how well you follow the instructions to answer the question.

        Response:
        {value}

        Question:
        {question}

        Your Answer:

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
        if provider == "openai":
            kwargs["api_key"] = get_call_kwarg("api_key") or os.environ.get(
                "OPENAI_API_KEY"
            )

        # 1. Get LLM response
        # Strip whitespace and convert to lowercase
        try:
            response = completion(model=self.llm_callable, messages=messages, **kwargs)
            response = response.choices[0].message.content  # type: ignore
            response = (response or "").strip().lower()
        except Exception as e:
            raise RuntimeError(f"Error getting response from the LLM: {e}") from e

        # 3. Return the response
        return response

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validation method for the ResponseEvaluator.


        Args:
            value (Any): The value to validate.
            metadata (Dict): The metadata for the validation.

        Returns:
            ValidationResult: The result of the validation.
        """
        # 1. Get the question and arg from the metadata
        validation_question = metadata.get("validation_question")
        if validation_question is None:
            raise RuntimeError(
                "'validation_question' missing from metadata. "
                "Please provide a question to prompt the LLM."
            )

        pass_on_invalid = metadata.get(
            "pass_on_invalid", False
        )  # Default behavior: Fail on an invalid response

        # 2. Setup the prompt
        prompt = self.get_validation_prompt(value, validation_question)

        # 3. Get the LLM response
        llm_response = self.get_llm_response(prompt)

        # 4. Check the LLM response and return the result
        if llm_response == "no":
            return FailResult(error_message="The LLM says 'No'. The validation failed.")

        if llm_response == "yes":
            return PassResult()

        # If the LLM generates an answer other than 'Yes' or 'No',
        # pass the validation, if the `pass_on_invalid` flag is set to True
        if pass_on_invalid:
            warn("The LLM returned an invalid answer. Passing the validation...")
            return PassResult()
        return FailResult(
            error_message="The LLM returned an invalid answer. Failing the validation..."
        )
