from typing import Any, Callable, Dict, List, Optional, Union

from guardrails_ai.restricttotopic import RestrictToTopic

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    register_validator,
)


@register_validator(name="guardrails/sensitive_topics", data_type="string")
class SensitiveTopic(RestrictToTopic):  # type: ignore
    """Checks if text contains any sensitive topics.

    Default behavior first runs a Zero-Shot model, and then falls back to
    ask OpenAI's `gpt-3.5-turbo` if the Zero-Shot model is not confident
    in the topic classification (score < 0.5).
    In our experiments this LLM fallback increases accuracy by 15% but also
    increases latency (more than doubles the latency in the worst case).
    Both the Zero-Shot classification and the GPT classification may be toggled.
    **Key Properties**
    | Property                      | Description                   |
    | ----------------------------- | ----------------------------- |
    | Name for `format` attribute   | `guardrails/sensitive_topics` |
    | Supported data types          | `string`                      |
    | Programmatic fix              | Prepends a trigger warning    |

    Args:
        sensitive_topics (List[str], Optional, defaults to [
            "holiday or anniversary of the trauma or loss",
            "certain sounds, sights, smells, or tastes related to the trauma",
            "loud voices or yelling",
            "loud noises",
            "arguments",
            "being ridiculed or judged",
            "being alone",
            "getting rejected",
            "being ignored",
            "breakup of a relationship",
            "violence in the news",
            "sexual harassment or unwanted touching",
            "physical illness or injury",
        ]): topics that the text should not contain.
        device (int, Optional, defaults to -1): Device ordinal for CPU/GPU
            supports for Zero-Shot classifier. Setting this to -1 will leverage
            CPU, a positive will run the Zero-Shot model on the associated CUDA
            device id.
        model (str, Optional, defaults to 'facebook/bart-large-mnli'): The
            Zero-Shot model that will be used to classify the topic. See a
            list of all models here:
            https://huggingface.co/models?pipeline_tag=zero-shot-classification
        llm_callable (Union[str, Callable, None], Optional, defaults to
            'gpt-3.5-turbo'): Either the name of the OpenAI model, or a callable
            that takes a prompt and returns a response.
        disable_classifier (bool, Optional, defaults to False): controls whether
            to use the Zero-Shot model. At least one of disable_classifier and
            disable_llm must be False.
        classifier_api_endpoint (str, Optional, defaults to None): An API endpoint
            to recieve post requests that will be used when provided. If not provided, a
            local model will be initialized.
        disable_llm (bool, Optional, defaults to False): controls whether to use
            the LLM fallback. At least one of disable_classifier and
            disable_llm must be False.
        zero_shot_threshold (float, Optional, defaults to 0.5): The threshold used to
            determine whether to accept a topic from the Zero-Shot model. Must be
            a number between 0 and 1.
        llm_threshold (int, Optional, defaults to 3): The threshold used to determine
        if a topic exists based on the provided llm api. Must be between 0 and 5.
    """

    def __init__(
        self,
        sensitive_topics: Optional[List[str]] = [],
        device: Optional[int] = -1,
        model: Optional[str] = "facebook/bart-large-mnli",
        llm_callable: Union[str, Callable, None] = None,
        disable_classifier: Optional[bool] = False,
        classifier_api_endpoint: Optional[str] = None,
        disable_llm: Optional[bool] = False,
        on_fail: Optional[Callable[..., Any]] = None,
        zero_shot_threshold: Optional[float] = 0.5,
        llm_threshold: Optional[int] = 3,
        **kwargs,
    ):
        if sensitive_topics is None:
            sensitive_topics = [
                "holiday or anniversary of the trauma or loss",
                "certain sounds, sights, smells, or tastes related to the trauma",
                "loud voices or yelling",
                "loud noises",
                "arguments",
                "being ridiculed or judged",
                "being alone",
                "getting rejected",
                "being ignored",
                "breakup of a relationship",
                "violence in the news",
                "sexual harassment or unwanted touching",
                "physical illness or injury",
            ]
        super().__init__(
            [],
            invalid_topics=sensitive_topics,
            device=device,
            model=model,
            disable_classifier=disable_classifier,
            classifier_api_endpoint=classifier_api_endpoint,
            disable_llm=disable_llm,
            llm_callable=llm_callable,
            on_fail=on_fail,
            zero_shot_threshold=zero_shot_threshold,
            llm_threshold=llm_threshold,
            **kwargs,
        )

    def get_args(self) -> Dict[str, Any]:
        # Overriding grandparent's get_args to avoid unnecessary arguments
        return {
            "sensitive_topics": self._kwargs.get("invalid_topics", None),
            "device": self._kwargs.get("device", -1),
            "model": self._kwargs.get("model", "facebook/bart-large-mnli"),
            "llm_callable": self._kwargs.get("llm_callable", None),
            "disable_classifier": self._kwargs.get("disable_classifier", False),
            "disable_llm": self._kwargs.get("disable_llm", False),
            "model_threshold": self._kwargs.get("model_threshold", 0.5),
        }

    def validate(
        self, value: str, metadata: Optional[Dict[str, Any]] = {}
    ) -> ValidationResult:
        """Validates that a string contains at least one valid topic and no invalid topics.

        Args:
            value (str): The given string to classify
            metadata (Optional[Dict[str, Any]], optional): _description_. Defaults to {}.

        Raises:
            ValueError: If a topic is invalid and valid
            ValueError: If no valid topics are set
            ValueError: If there is no llm or zero shot classifier set

        Returns:
            ValidationResult: PassResult if a topic is restricted and valid,
            FailResult otherwise
        """
        # Verify at least one invalid topic exists.
        invalid_topics = list(set(self._invalid_topics))
        if not invalid_topics:
            raise ValueError("A set of invalid topics must be provided.")

        # Ensemble method
        if not self._disable_classifier and not self._disable_llm:
            found_topics = self.get_topics_ensemble(value, invalid_topics)
        # LLM Classifier Only
        elif self._disable_classifier and not self._disable_llm:
            found_topics = self.get_topics_llm(value, invalid_topics)
        # Zero Shot Classifier Only
        elif not self._disable_classifier and self._disable_llm:
            found_topics = self.get_topics_zero_shot(value, invalid_topics)
        else:
            raise ValueError("Either classifier or llm must be enabled.")

        # Determine if invalid topics were found
        invalid_topics_found = [
            topic for topic in found_topics if topic in self._invalid_topics
        ]

        # Require at least one valid topic and no invalid topics
        if invalid_topics_found:
            return FailResult(
                error_message=f"Invalid topics found: {invalid_topics_found}"
            )

        return PassResult()
