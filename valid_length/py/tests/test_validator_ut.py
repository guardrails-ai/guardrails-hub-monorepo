from guardrails.validator_base import PassResult, FailResult
from guardrails_ai.valid_length import ValidLength


class TestStringValue:
    def test_happy_path(self):
        """Test the happy path for the validator."""
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate("hello", {})
        assert isinstance(result, PassResult)

    def test_fail_path_empty(self):
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate("", {})
        assert isinstance(result, FailResult)
        assert isinstance(result.fix_value, str)
        assert len(result.fix_value) == 3

    def test_fail_path_too_short(self):
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate("hi", {})
        assert isinstance(result, FailResult)
        assert result.fix_value == "hii"

    def test_fail_path_too_long(self):
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate("hello there!", {})
        assert isinstance(result, FailResult)
        assert result.fix_value == "hello "


class TestListValue:
    def test_happy_path(self):
        """Test the happy path for the validator."""
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate(["Hello", "there!", "General"], {})
        assert isinstance(result, PassResult)

    def test_fail_path_empty(self):
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate([], {})
        assert isinstance(result, FailResult)
        assert isinstance(result.fix_value, list)
        assert len(result.fix_value) == 3

    def test_fail_path_too_short(self):
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate(["Hello", "there!"], {})
        assert isinstance(result, FailResult)
        assert result.fix_value == ["Hello", "there!", "there!"]

    def test_fail_path_too_long(self):
        validator = ValidLength(min=3, max=6, on_fail="fix")
        result = validator.validate(
            ["General", "Kenobi,", "you", "are", "a", "bold", "one!"], {}
        )
        assert isinstance(result, FailResult)
        assert result.fix_value == ["General", "Kenobi,", "you", "are", "a", "bold"]
