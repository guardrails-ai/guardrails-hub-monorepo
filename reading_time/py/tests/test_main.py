from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.reading_time import ReadingTime
import pytest


FIVE_SECONDS = 5 / 60  # 5 seconds in minutes


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[ReadingTime(reading_time=FIVE_SECONDS, on_fail="exception")]
    )


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
          "text": "Meditation is peaceful and calming after taking a long uninterrupted walk."
        }
        """
    ],
)
def test_happy_path(value):
    """Test the happy path for the validator."""
    # Create a guard from the pydantic model
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)
    response = guard.parse(value)
    print("Happy path response", response)
    assert response.validation_passed is True


# Test fail path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
          "text": "Mammals are the vertebrates within the class Mammalia, a clade of endothermic amniotes distinguished from reptiles by the possession of a neocortex, hair, three middle ear bones, and mammary glands. Reproduction in mammals is typically viviparous, with the fetus developing within the mother's uterus. On the other hand, reptiles are tetrapod animals in the class Reptilia, comprising today's turtles, crocodilians, snakes, amphisbaenians, lizards, tuatara, and their extinct relatives. The study of these traditional reptile orders, historically combined with that of modern amphibians, is called herpetology. Amphibians are ectothermic, tetrapod vertebrates of the class Amphibia. Modern amphibians are all Lissamphibia. They inhabit a wide variety of habitats, with most species living within terrestrial, fossorial, arboreal or freshwater aquatic ecosystems. Thus, amphibians typically start out as larvae living in water, but some species have developed behavioural adaptations to bypass this." 
        }
        """
    ],
)
def test_fail_path(value):
    # Create a guard from the pydantic model
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)

    with pytest.raises(Exception):
        response = guard.parse(value)
        print("Fail path response", response)
