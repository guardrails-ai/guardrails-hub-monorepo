import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Protocol

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from nace_sdk import NaceClient, Noul, NoulAnswer, RetryPolicy, Score, ScoreAnswer

VERSION = "0.1.0"
CLIENT_INFO = f"drex-policy/{VERSION}"
DEFAULT_MODEL = "drex-v2.0"
IMAGE_MODEL = "drex-max"
MAX_IMAGES = 8

Question = Noul | Score


class DrexPolicyError(Exception):
    """Drex could not decide the check. This is not a policy fail."""


class SystemOneCaller(Protocol):
    def system_one(
        self,
        state: str,
        questions: Mapping[str, Question],
        *,
        model: str | None = None,
        images: Sequence[str] | None = None,
    ) -> Any: ...


@register_validator(name="nace/drex_policy", data_type="string")
class DrexPolicy(Validator):
    """Validates a string by asking Drex one `noul` or `score` question about it.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `nace/drex_policy`                |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |

    Args:
        question (Noul | Score): The Drex question asked about the value.
        fail_at (float): For a noul, the P(yes) threshold in [0, 1]. For a score,
            the expected-index threshold.
        fail_when (str): "yes" (default) or "no" for a noul. "at_or_above"
            (default) or "below" for a score.
        question_id (str): Key of the question in the Drex request. Default "policy".
        model (str): Drex model id. Default "drex-v2.0". Images need "drex-max".
        client (NaceClient): An existing client. Omit it to build one from
            `NACE_API_KEY` and `NACE_BASE_URL`.
    """

    def __init__(
        self,
        question: Question,
        fail_at: float,
        fail_when: str | None = None,
        question_id: str = "policy",
        model: str | None = None,
        client: SystemOneCaller | None = None,
        on_fail: Callable | None = None,
        **kwargs: Any,
    ):
        if not isinstance(question, (Noul, Score)):
            raise TypeError("question must be a nace_sdk.Noul or nace_sdk.Score")
        if not isinstance(question_id, str) or not question_id:
            raise ValueError("question_id must be a non-empty string")
        if isinstance(fail_at, bool) or not isinstance(fail_at, (int, float)):
            raise TypeError("fail_at must be a number")
        if model is not None and (not isinstance(model, str) or not model):
            raise ValueError("model must be a non-empty string")
        if isinstance(question, Noul):
            fail_when = "yes" if fail_when is None else fail_when
            if fail_when not in ("yes", "no"):
                raise ValueError("noul fail_when must be 'yes' or 'no'")
            if not 0.0 <= fail_at <= 1.0:
                raise ValueError("noul fail_at must be between 0 and 1")
        else:
            fail_when = "at_or_above" if fail_when is None else fail_when
            if fail_when not in ("at_or_above", "below"):
                raise ValueError("score fail_when must be 'at_or_above' or 'below'")
            if not math.isfinite(fail_at):
                raise ValueError("score fail_at must be finite")
        super().__init__(
            on_fail=on_fail,
            question=question.model_dump(mode="json"),
            fail_at=fail_at,
            fail_when=fail_when,
            question_id=question_id,
            model=model,
            **kwargs,
        )
        self._question = question
        self._fail_at = float(fail_at)
        self._fail_when = fail_when
        self._question_id = question_id
        self._model = model
        self._client = client

    def _get_client(self) -> SystemOneCaller:
        if self._client is None:
            self._client = NaceClient(
                client_info=CLIENT_INFO,
                timeout=60,
                retry=RetryPolicy(timeout=180),
            )
        return self._client

    def _model_for(self, images: Sequence[str] | None) -> str:
        if not images:
            return self._model or DEFAULT_MODEL
        if self._model != IMAGE_MODEL:
            requested = self._model or DEFAULT_MODEL
            raise DrexPolicyError(
                f"images require model {IMAGE_MODEL!r}, not {requested!r}"
            )
        if len(images) > MAX_IMAGES:
            raise DrexPolicyError(f"{IMAGE_MODEL} accepts at most {MAX_IMAGES} images")
        return IMAGE_MODEL

    def validate(
        self, value: Any, metadata: dict[str, Any] | None = None
    ) -> ValidationResult:
        """Asks Drex the question about `value` and compares the answer with `fail_at`."""
        if not isinstance(value, str):
            raise TypeError("drex_policy validates a string")
        images = (metadata or {}).get("images")
        if images is not None and (
            isinstance(images, str)
            or not isinstance(images, (list, tuple))
            or not all(isinstance(image, str) and image for image in images)
        ):
            raise TypeError("metadata['images'] must be a list of non-empty strings")
        model = self._model_for(images)
        response = self._get_client().system_one(
            value,
            {self._question_id: self._question},
            model=model,
            images=list(images) if images else None,
        )
        answer = _answer(response, self._question_id, self._question)
        if isinstance(answer, NoulAnswer):
            label, measured = "P(yes)", float(answer.noul)
            fail_low = self._fail_when == "no"
        else:
            label, measured = "score", float(answer.score)
            fail_low = self._fail_when == "below"
        failed = measured < self._fail_at if fail_low else measured >= self._fail_at
        result_metadata = {
            "drex_model": model,
            "drex_question_id": self._question_id,
            "drex_answer": answer.model_dump(mode="json"),
        }
        if failed:
            relation = "<" if fail_low else ">="
            return FailResult(
                error_message=f"Drex {label}={measured} {relation} fail_at={self._fail_at}",
                metadata=result_metadata,
            )
        return PassResult(metadata=result_metadata)


def _answer(
    response: Any, question_id: str, question: Question
) -> NoulAnswer | ScoreAnswer:
    answers = getattr(response, "answers", None)
    if not isinstance(answers, Mapping) or question_id not in answers:
        raise DrexPolicyError(f"Drex response has no answer for {question_id!r}")
    answer = answers[question_id]
    expected = NoulAnswer if isinstance(question, Noul) else ScoreAnswer
    if not isinstance(answer, expected):
        raise DrexPolicyError(
            f"Drex answer for {question_id!r} is {type(answer).__name__}, expected {expected.__name__}"
        )
    return answer
