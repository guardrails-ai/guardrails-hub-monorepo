import json
from typing import Any

import pytest
from guardrails import Guard
from nace_sdk import Noul, RetryPolicy, Score, SystemOneResponse

from guardrails_ai.drex_policy import DrexPolicy
from guardrails_ai.drex_policy.main import CLIENT_INFO, DrexPolicyError


class FakeClient:
    def __init__(self, answer: dict) -> None:
        self.answer = answer
        self.calls: list[Any] = []

    def system_one(self, state, questions, *, model=None, images=None):
        self.calls.append((state, questions, model, images))
        return SystemOneResponse.model_validate_json(
            json.dumps(
                {
                    "model": model,
                    "usage": {"input_tokens": 4, "image_tokens": 0, "output_tokens": 1},
                    "answers": {"policy": self.answer},
                }
            )
        )


def noul(probability: float) -> FakeClient:
    return FakeClient({"type": "noul", "noul": probability})


def score(value: float) -> FakeClient:
    return FakeClient(
        {
            "type": "score",
            "score": value,
            "confidence": 0.8,
            "legend": ["none", "low", "high"],
            "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7},
        }
    )


TOXIC = Noul(instructions="Is this text toxic?")


def guard(client: FakeClient, model: str | None = None) -> Guard:
    return Guard().use(
        DrexPolicy(
            question=TOXIC, fail_at=0.5, model=model, client=client, on_fail="exception"
        )
    )


def test_pass():
    client = noul(0.1)
    result = guard(client).validate("hello")
    assert result.validation_passed is True
    assert result.validated_output == "hello"
    assert client.calls == [("hello", {"policy": TOXIC}, "drex-v2.0", None)]


def test_fail():
    with pytest.raises(Exception) as exc_info:
        guard(noul(0.9)).validate("you idiot")
    assert str(exc_info.value) == (
        "Validation failed for field with errors: Drex P(yes)=0.9 >= fail_at=0.5"
    )


def test_fail_when_no():
    validator = DrexPolicy(
        question=TOXIC, fail_at=0.5, fail_when="no", client=noul(0.1)
    )
    result = validator.validate("hello", {})
    assert result.outcome == "fail"
    assert result.error_message == "Drex P(yes)=0.1 < fail_at=0.5"


def test_fail_keeps_answer_in_metadata():
    validator = DrexPolicy(question=TOXIC, fail_at=0.5, client=noul(0.9))
    result = validator.validate("you idiot", {})
    assert result.outcome == "fail"
    assert result.metadata == {
        "drex_model": "drex-v2.0",
        "drex_question_id": "policy",
        "drex_answer": {"type": "noul", "noul": 0.9},
    }


def test_score_at_or_above_and_below():
    question = Score(instructions="How toxic?", criteria=["none", "low", "high"])
    high = DrexPolicy(question=question, fail_at=1.5, client=score(2.0))
    assert high.validate("x", {}).outcome == "fail"
    below = DrexPolicy(
        question=question, fail_at=1.5, fail_when="below", client=score(2.0)
    )
    assert below.validate("x", {}).outcome == "pass"


def test_drex_latest_is_forwarded_unchanged():
    client = noul(0.1)
    guard(client, model="drex-latest").validate("hello")
    assert client.calls[0][2] == "drex-latest"


def test_images_go_to_drex_max():
    client = noul(0.1)
    validator = DrexPolicy(question=TOXIC, fail_at=0.5, model="drex-max", client=client)
    validator.validate("caption", {"images": ["data:image/png;base64,AAAA"]})
    assert client.calls[0][2:] == ("drex-max", ["data:image/png;base64,AAAA"])


@pytest.mark.parametrize("model", [None, "drex-v2.0", "drex-latest"])
def test_images_without_drex_max_are_refused(model):
    client = noul(0.1)
    validator = DrexPolicy(question=TOXIC, fail_at=0.5, model=model, client=client)
    with pytest.raises(DrexPolicyError, match="images require model 'drex-max'"):
        validator.validate("caption", {"images": ["data:image/png;base64,AAAA"]})
    assert client.calls == []


def test_more_than_eight_images_are_refused():
    client = noul(0.1)
    validator = DrexPolicy(question=TOXIC, fail_at=0.5, model="drex-max", client=client)
    with pytest.raises(DrexPolicyError, match="at most 8 images"):
        validator.validate("caption", {"images": ["data:image/png;base64,AAAA"] * 9})
    assert client.calls == []


def test_omitted_instructions_stay_none():
    client = noul(0.1)
    DrexPolicy(question=Noul(), fail_at=0.5, client=client).validate("hello", {})
    sent = client.calls[0][1]["policy"]
    assert sent.instructions is None
    assert sent.model_dump(exclude_none=True) == {"type": "noul"}


def test_built_client_settings(monkeypatch):
    seen = {}

    class Recorder:
        def __init__(self, **kwargs):
            seen.update(kwargs)

    monkeypatch.setattr("guardrails_ai.drex_policy.main.NaceClient", Recorder)
    DrexPolicy(question=TOXIC, fail_at=0.5)._get_client()
    assert seen["client_info"] == CLIENT_INFO == "drex-policy/0.1.0"
    assert seen["timeout"] == 60
    assert seen["retry"] == RetryPolicy(timeout=180)
    assert "model" not in seen


@pytest.mark.parametrize(
    "kwargs",
    [
        {"fail_at": 1.5},
        {"fail_at": 0.5, "fail_when": "below"},
        {"fail_at": 0.5, "question_id": ""},
        {"fail_at": 0.5, "model": ""},
    ],
)
def test_bad_config(kwargs):
    with pytest.raises(ValueError):
        DrexPolicy(question=TOXIC, **kwargs)
