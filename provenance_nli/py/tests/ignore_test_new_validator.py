import unittest
from guardrails_ai.provenance_nli import ProvenanceNLI
from guardrails.validator_base import PassResult, FailResult


# TODO: Turn this into an integration test
class TestProvenanceNLI(unittest.TestCase):
    def setUp(self):
        # Assuming the model is already loaded elsewhere and passed here as a parameter
        self.validator = ProvenanceNLI(
            model_name="model_name", model_checkpoint_path="model_checkpoint_path"
        )

    def test_validator_with_valid_input(self):
        # Assuming 'context' and 'input_sentence' are provided correctly
        context = "This is a context sentence."
        input_sentence = "This sentence is related to the context."
        result = self.validator.validate(input_sentence, {"context": context})
        self.assertIsInstance(result, PassResult)

    def test_validator_with_invalid_input(self):
        # Assuming 'context' and 'input_sentence' are provided correctly
        context = "This is a context sentence."
        input_sentence = "This sentence is unrelated to the context."
        result = self.validator.validate(input_sentence, {"context": context})
        self.assertIsInstance(result, FailResult)


if __name__ == "__main__":
    unittest.main()
