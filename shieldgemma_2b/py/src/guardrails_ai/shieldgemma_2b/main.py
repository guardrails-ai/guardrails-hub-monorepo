import json
from typing import Any, Callable, Dict, List, Optional
from guardrails.validator_base import ErrorSpan

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from guardrails.logger import logger

_MODEL_NAME = "google/shieldgemma-2b"

# Safety guidelines ShieldGemma is prompted with, keyed by this validator's
# POLICY__* constants. Text follows the official ShieldGemma model card.
_POLICY_GUIDELINES = {
    "NO_DANGEROUS_CONTENT": (
        '"No Dangerous Content": The chatbot shall not generate content that '
        "harming oneself and/or others (e.g., accessing or building firearms "
        "and explosive devices, promotion of terrorism, instructions for suicide)."
    ),
    "NO_HARASSMENT": (
        '"No Harassment": The chatbot shall not generate content that is '
        "malicious, intimidating, bullying, or abusive content targeting "
        "another individual (e.g., physical threats, denial of tragic events, "
        "disparaging victims of violence)."
    ),
    "NO_HATE_SPEECH": (
        '"No Hate Speech": The chatbot shall not generate content that '
        "targeting identity and/or protected attributes (e.g., racial slurs, "
        "promotion of discrimination, calls to violence against protected "
        "groups) or dehumanizing/belittling/vilifying on the basis of race, "
        "ethnicity, religion, disability, age, nationality, veteran status, "
        "sexual orientation, gender, gender identity, caste, or any other "
        "protected status."
    ),
    "NO_SEXUAL_CONTENT": (
        '"No Sexually Explicit Information": The chatbot shall not generate '
        "content that contains references to sexual acts or other lewd content "
        "(e.g., sexually graphic descriptions). Medical or scientific terms "
        "related to human anatomy or sex education are permitted."
    ),
}


@register_validator(name="guardrails/shieldgemma_2b", data_type="string")
class ShieldGemma2B(Validator):
    """
    Classifies model inputs or outputs as "safe" or "unsafe" based on certain policies defined by the ShieldGemma-2B model.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/shieldgemma_2b`        |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |

    Args:
        policies (List[str]): A list of policies that can be either `ShieldGemma2B.POLICY__NO_DANGEROUS_CONTENT`, `ShieldGemma2B.POLICY__NO_HARASSMENT`, `ShieldGemma2B.POLICY__NO_HATE_SPEECH`, and `ShieldGemma2B.POLICY__NO_SEXUAL_CONTENT`.
        score_threshold (float): Threshold score for the classification. If the score is above this threshold, the input is considered unsafe.
    """  # noqa

    POLICY__NO_DANGEROUS_CONTENT = "NO_DANGEROUS_CONTENT"
    POLICY__NO_HARASSMENT = "NO_HARASSMENT"
    POLICY__NO_HATE_SPEECH = "NO_HATE_SPEECH"
    POLICY__NO_SEXUAL_CONTENT = "NO_SEXUAL_CONTENT"

    def __init__(
        self,
        policies: Optional[List[str]] = None,
        validation_method: Optional[str] = "full",
        score_threshold: Optional[float] = None,
        on_fail: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(
            on_fail=on_fail,
            validation_method=validation_method,
            **kwargs,
        )

        self._policies = policies
        self.score_threshold = score_threshold

        if isinstance(policies, list) and len(policies) == 0:
            raise ValueError("Policies cannot be empty. Please provide one policy.")

        if policies and isinstance(policies, list) and len(policies) > 1:
            logger.warn(
                (
                    "GemmaShield2B Validator: Multiple policies are not officially supported"
                    "it is recommended to use one policy at a time."
                    "Refer to: https://huggingface.co/google/shieldgemma-2b/discussions/11"
                )
            )

        # Lazily-loaded local model + tokenizer (only used when use_local=True).
        self._tokenizer = None
        self._model = None

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        if not value:
            raise ValueError("Value cannot be empty.")

        (classification, score) = self._inference(value)

        is_unsafe = classification == "unsafe"

        if is_unsafe:
            error_span = ErrorSpan(
                start=0,
                end=len(value),
                reason=f"Unsafe content: {value}",
            )
            return FailResult(
                error_message=(
                    f"Prompt contains unsafe content. Classification: {classification}, Score: {score}"
                ),
                error_spans=[error_span],
            )
        else:
            return PassResult()

    def _load_model(self):
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        self._model = AutoModelForCausalLM.from_pretrained(
            _MODEL_NAME,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        )
        self._model.eval()

    def _guideline(self) -> str:
        policy = self._policies[0] if self._policies else "NO_DANGEROUS_CONTENT"
        return _POLICY_GUIDELINES.get(
            policy, _POLICY_GUIDELINES["NO_DANGEROUS_CONTENT"]
        )

    def _inference_local(self, model_input: Any):
        """Classify `model_input` as safe/unsafe by running ShieldGemma-2B locally.

        Returns (classification, score) where score is P(policy violated).
        """
        import torch

        self._load_model()
        assert self._tokenizer is not None and self._model is not None

        chat = [{"role": "user", "content": str(model_input)}]
        inputs = self._tokenizer.apply_chat_template(
            chat,
            guideline=self._guideline(),
            return_tensors="pt",
            return_dict=True,
        )

        with torch.no_grad():
            logits = self._model(**inputs).logits

        # ShieldGemma answers "Yes" (violates policy) or "No"; the violation
        # probability is the softmax over those two vocab logits.
        vocab = self._tokenizer.get_vocab()
        yes_no_ids = [vocab["Yes"], vocab["No"]]
        selected = logits[0, -1, yes_no_ids]
        probs = torch.softmax(selected.float(), dim=0)
        score = float(probs[0].item())

        threshold = self.score_threshold if self.score_threshold is not None else 0.5
        classification = "unsafe" if score >= threshold else "safe"
        return (classification, score)

    def _inference_remote(self, model_input: Any) -> Any:
        """Remote inference method for this validator."""
        request_body = {
            "policies": self._policies,
            "score_threshold": self.score_threshold,
            "chat": [{"role": "user", "content": model_input}],
        }

        validation_endpoint = self.validation_endpoint
        if validation_endpoint is None:
            raise RuntimeError("No validation endpoint set for remote inference.")

        response = self._hub_inference_request(
            json.dumps(request_body), validation_endpoint
        )

        status = response.get("status")
        if status != 200:
            detail = response.get("response", {}).get("detail", "Unknown error")
            raise ValueError(
                f"Failed to get valid response from ShieldGemma-2B model. Status: {status}. Detail: {detail}"
            )

        response_data = response.get("response")

        classification = response_data.get("class")
        score = response_data.get("score")

        return (classification, score)
