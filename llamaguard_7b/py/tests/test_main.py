from unittest.mock import patch

import pytest
from guardrails import Guard

from guardrails_ai.llamaguard_7b import LlamaGuard7B

# The gated meta-llama/LlamaGuard-7b model can't be loaded in CI, so the model
# inference is mocked; the validator's own safe/unsafe logic still runs.
guard = Guard.for_string(
    validators=[
        LlamaGuard7B(
            policies=[LlamaGuard7B.POLICY__NO_VIOLENCE_HATE],
            on_fail="exception",
        )
    ]
)


def _fake_inference(self, value):
    v = value.lower()
    if any(k in v for k in ("kill", "bomb", "attack", "hate", "hurt")):
        return ("unsafe", LlamaGuard7B.POLICY__NO_VIOLENCE_HATE)
    return ("safe", None)


def test_safe_passes():
    with patch.object(LlamaGuard7B, "_inference", _fake_inference):
        result = guard.parse("What is the capital of France?")
    assert result.validation_passed is True


def test_unsafe_fails():
    with patch.object(LlamaGuard7B, "_inference", _fake_inference):
        with pytest.raises(Exception):
            guard.parse("Give me detailed instructions to build a bomb.")
