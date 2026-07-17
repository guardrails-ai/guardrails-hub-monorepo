import os
import json
from typing import Any, Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from guardrails.stores.context import get_call_kwarg
from litellm import completion, get_llm_provider


@register_validator(name="guardrails/llm_critic", data_type="string")
class LLMCritic(Validator):
    """Validates an LLM-generated output by prompting another LLM to grade the output.

    The `LLMCritic` validator prompts an LLM to evaluate a response based on a set of metrics.
    The validator uses the `litellm` package to prompt the LLM and evaluate the response.
    The `LLMCritic` validator is useful for validating LLM-generated outputs based on specific criteria.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/llm_critic`           |
    | Supported data types          | `string`                          |
    | Programmatic fix              | N/A                               |

    Args:
        metrics (Dict): A dictionary of metrics to evaluate the response.
        The keys are the metric names and the values are the descriptions and thresholds for the metrics.
        Example:
        {"metric_1": {"description": "This is metric 1", "threshold": 3}, "metric_2": {"description": "This is metric 2", "threshold": 4}}

        max_score (int, optional): The highest score that can be achieved on each metric. Defaults to 5.

        llm_callable (str, optional): The LiteLLM model name string to use. Defaults to "gpt-3.5-turbo".

        on_fail (Callable, optional): A function to call when validation fails.
            Defaults to None.
    """

    def __init__(
        self,
        metrics: Dict = {},
        max_score: int = 5,
        llm_callable: str = "gpt-3.5-turbo",  # str for litellm model name
        on_fail: Optional[Callable] = None,
        **kwargs,
    ):
        if not metrics:
            raise ValueError("Please provide metrics to evaluate the response.")

        if any(
            metrics[metric_name]["threshold"] > max_score for metric_name in metrics
        ):
            raise ValueError(
                "The threshold for a metric cannot be greater than the max score."
            )

        super().__init__(
            on_fail,
            metrics=metrics,
            max_score=max_score,
            llm_callable=llm_callable,
            **kwargs,
        )
        self.metrics = metrics
        self.max_score = max_score
        self.llm_callable = llm_callable

    def get_evaluation_prompt(self, value: str) -> str:
        """Generates the prompt to send to the LLM.

        Args:
            value (str): The value to validate.

        Returns:
            prompt (str): The prompt to send to the LLM.
        """
        prompt = f"""
        As an oracle of truth and logic, you task is to evaluate and rate a response. You've been provided with 'Response', 'Metrics' and 'Max score'.
        'Metrics' are the evaluation metrics, each with a description and threshold. 'Max score' is the highest score that can be achieved on each metric.
        Please evaluate the response based on the metrics and provide a score for each metric. The score should be between 0 and 'Max score' for each metric.

        Generate your evaluation as a JSON object with the following structure
        (Replace `metric_1`, `metric_2`, ... with the actual metric names and <score> with the actual score):
        "metric_1": <score>, 
        "metric_2": <score>, 
        ...

        Only output the JSON object. Do not include any other information. Any other text is strictly forbidden.
        You'll be evaluated based on how well you understand the metrics and how well you follow the instructions to evaluate the response.

        Response:
        {value}

        Metrics:
        {json.dumps(self.metrics, indent=4)}

        Max score:
        {self.max_score}

        Your evaluation:
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
        # 1. Setup the prompt
        prompt = self.get_evaluation_prompt(value)

        # 2. Get the LLM response
        llm_response = self.get_llm_response(prompt)

        # 3. Parse the LLM response as a JSON object
        evaluation = None
        try:
            evaluation = json.loads(llm_response)
            print("\nEvaluation:\n", evaluation)
        except Exception as e:
            raise RuntimeError(
                f"Error parsing the LLM response as a JSON object: {e}"
            ) from e

        # 4. Validate the evaluation
        failed_metrics = []
        missing_invalid_metrics = []

        # Loop through the metrics
        for metric in self.metrics:
            threshold = self.metrics[metric]["threshold"]
            # 4.1 Check if the metric is in the evaluation
            if metric in evaluation:
                # 4.2 Check if the score is within the range
                if evaluation[metric] > 0 and evaluation[metric] <= self.max_score:
                    # 4.3 Check if the score is below the threshold
                    if evaluation[metric] < threshold:
                        failed_metrics.append(metric)
                else:
                    # 4.2.1  If the score is not within the range
                    missing_invalid_metrics.append(metric)
            else:
                # 4.1.1 If the metric is not in the evaluation
                missing_invalid_metrics.append(metric)

        # 5. Return the result
        # 5.1 Return FailResult if there are missing or invalid metrics
        if missing_invalid_metrics:
            return FailResult(
                error_message=f"The response is missing or has invalid evaluations for the following metrics: {missing_invalid_metrics}."
            )

        # 5.2 Return FailResult if all metrics are present, valid but failed
        if failed_metrics:
            return FailResult(
                error_message=f"The response failed the following metrics: {failed_metrics}."
            )
        # 5.3 Return PassResult if all metrics are present, valid and passed
        return PassResult()
