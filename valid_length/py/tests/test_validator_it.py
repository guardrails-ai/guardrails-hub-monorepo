from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.valid_length import ValidLength
import pytest


# Create a pydantic model with a field that uses the validator
class ValidatorTestObjectString(BaseModel):
    text: str = Field(validators=[ValidLength(min=3, max=6, on_fail="exception")])


class TestStringValue:
    # Test happy path
    @pytest.mark.parametrize(
        "value",
        [
            """
            {
                "text": "hello"
            }
            """
        ],
    )
    def test_happy_path(self, value):
        """Test the happy path for the validator."""
        # Create a guard from the pydantic model
        guard = Guard.for_pydantic(output_class=ValidatorTestObjectString)
        response = guard.parse(value)
        print("Happy path response", response)
        assert response.validation_passed is True

    # Test fail path
    @pytest.mark.parametrize(
        "value",
        [
            """
            {
                "text": "hi"
            }
            """,
            """
            {
                "text": "educational"
            }
            """,
        ],
    )
    def test_fail_path(self, value):
        # Create a guard from the pydantic model
        guard = Guard.for_pydantic(output_class=ValidatorTestObjectString)

        with pytest.raises(Exception):
            response = guard.parse(value)
            print("Fail path response", response)


class ValidatorTestObjectList(BaseModel):
    my_list: list[str] = Field(
        validators=[ValidLength(min=3, max=6, on_fail="exception")]
    )


class TestListValue:
    # Test happy path
    @pytest.mark.parametrize(
        "value",
        [
            """
            {
                "my_list": ["Hello", "there!", "General"]
            }
            """
        ],
    )
    def test_happy_path(self, value):
        """Test the happy path for the validator."""
        # Create a guard from the pydantic model
        guard = Guard.for_pydantic(output_class=ValidatorTestObjectList)
        response = guard.parse(value)
        print("Happy path response", response)
        assert response.validation_passed is True

    # Test fail path
    @pytest.mark.parametrize(
        "value",
        [
            """
            {
                "my_list": ["Hello", "there!"]
            }
            """,
            """
            {
                "my_list": ["General", "Kenobi,", "you", "are", "a", "bold", "one!"]
            }
            """,
        ],
    )
    def test_fail_path(self, value):
        # Create a guard from the pydantic model
        guard = Guard.for_pydantic(output_class=ValidatorTestObjectList)

        with pytest.raises(Exception):
            response = guard.parse(value)
            print("Fail path response", response)
