import unittest
from unittest.mock import MagicMock, patch
import torch
from guardrails_ai.provenance_nli import ProvenanceNLI


class TestProvenanceNLI(unittest.TestCase):
    @patch("transformers.AutoModelForSequenceClassification.from_pretrained")
    @patch("transformers.AutoTokenizer.from_pretrained")
    @patch("torch.load")
    def setUp(self, mocked_torch_load, mocked_tokenizer, mocked_model):
        mocked_model.return_value = MagicMock()
        mocked_tokenizer.return_value = MagicMock()
        mocked_torch_load.return_value = MagicMock()
        self.validator = ProvenanceNLI(
            model_name="dummy-model",
            model_checkpoint_path="dummy-checkpoint",
            top_k=1,
            max_length=256,
        )
        self.validator._tokenizer.encode_plus.return_value = {
            "input_ids": [0, 1, 2],
            "attention_mask": [1, 1, 1],
            "token_type_ids": [0, 0, 0],
        }
        logits_mock = torch.tensor([[-1, 0, 1]])
        self.validator._model.return_value = MagicMock(logits=logits_mock)

    def test_initialization(self):
        self.assertIsNotNone(self.validator)

    def test_query_function(self):
        metadata = {
            "sources": ["source1", "source2"],
            "chunk_strategy": "sentence",
            "embed_function": lambda x: x,
        }
        query_function = self.validator.get_query_function(metadata)
        self.assertIsNotNone(query_function)

    @patch("guardrails_ai.provenance_nli.ProvenanceNLI.get_model_prediction")
    def test_model_prediction(self, mocked_get_model_prediction):
        mocked_get_model_prediction.return_value = ("entailment", 0.9)
        prediction = self.validator.get_model_prediction(
            "test sentence", "test hypothesis"
        )
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction, ("entailment", 0.9))

    @patch("guardrails_ai.provenance_nli.ProvenanceNLI.get_nli_evaluation")
    def test_nli_evaluation(self, mocked_get_nli_evaluation):
        mocked_get_nli_evaluation.return_value = [("context", 0.9)]
        evaluation = self.validator.get_nli_evaluation(
            "test sentence", ["context"], {"metadata": "test"}
        )
        self.assertIsNotNone(evaluation)
        self.assertEqual(evaluation, [("context", 0.9)])

    @patch("guardrails_ai.provenance_nli.ProvenanceNLI.validate_each_sentence")
    def test_sentence_validation(self, mocked_validate_each_sentence):
        mocked_validate_each_sentence.return_value = "valid"
        result = self.validator.validate_each_sentence(
            "test sentence", lambda text: text, {}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, "valid")

    @patch("guardrails_ai.provenance_nli.ProvenanceNLI.query_vector_collection")
    def test_vector_collection_query(self, mocked_query_vector_collection):
        mocked_query_vector_collection.return_value = [("source1", 0.1)]
        top_chunks = self.validator.query_vector_collection(
            text="test sentence",
            k=1,
            sources=["source1", "source2"],
            embed_function=lambda text: (
                [0.1, 0.2] if isinstance(text, str) else [[0.1, 0.2]] * len(text)
            ),
        )
        self.assertIsNotNone(top_chunks)
        self.assertEqual(top_chunks, [("source1", 0.1)])


if __name__ == "__main__":
    unittest.main()
