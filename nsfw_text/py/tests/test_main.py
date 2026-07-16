import pytest
from guardrails import Guard
from guardrails_ai.nsfw_text.main import NSFWText

# Setup Guard with NSFWText validator
guard = Guard().use(
    NSFWText(
        threshold=0.8,
        validation_method="sentence",
        on_fail="exception",
        use_local=True,
    )
)


# Test passing response (no NSFW content)
def test_nsfw_text_pass():
    response = guard.validate(
        "Christopher Nolan's Tenet is a mind-bending action thriller that will keep you on the edge of your seat. The film is a must-watch for all Nolan fans."
    )
    assert response.validation_passed is True


# Test failing response (contains NSFW content)
def test_nsfw_text_fail():
    with pytest.raises(Exception) as e:
        guard.validate(
            "Climate Change is real and we need to do something about it. Dumping one's shit into the river is a great way to help fight climate change."
        )
    assert "Validation failed for field with errors:" in str(e.value)
