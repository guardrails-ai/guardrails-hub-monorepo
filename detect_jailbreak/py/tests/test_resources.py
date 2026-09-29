from unittest.mock import MagicMock, patch

from guardrails_ai.detect_jailbreak.resources import (
    _load_sanitized_config,
    load_text_classification_pipeline,
)


# Mirrors the real, broken config published by zhx123/ftrobertallm: id2label
# values are ints instead of strings, which huggingface_hub's strict
# PretrainedConfig validation rejects outright.
_MALFORMED_CONFIG_DICT = {
    "model_type": "roberta",
    "id2label": {"0": 0, "1": 1},
    "label2id": {"0": 0, "1": 1},
}


def test_load_sanitized_config_stringifies_id2label_and_label2id():
    with patch(
        "guardrails_ai.detect_jailbreak.resources.PretrainedConfig.get_config_dict",
        return_value=(dict(_MALFORMED_CONFIG_DICT), {}),
    ):
        config = _load_sanitized_config("zhx123/ftrobertallm")

    assert config.id2label == {0: "0", 1: "1"}
    assert config.label2id == {"0": "0", "1": "1"}


def test_load_sanitized_config_leaves_well_formed_labels_untouched():
    well_formed = {
        "model_type": "roberta",
        "id2label": {"0": "safe", "1": "jailbreak"},
        "label2id": {"safe": 0, "jailbreak": 1},
    }
    with patch(
        "guardrails_ai.detect_jailbreak.resources.PretrainedConfig.get_config_dict",
        return_value=(dict(well_formed), {}),
    ):
        config = _load_sanitized_config("some/well-formed-model")

    assert config.id2label == {0: "safe", 1: "jailbreak"}
    assert config.label2id == {"safe": "0", "jailbreak": "1"}


def test_load_text_classification_pipeline_passes_sanitized_config_through():
    fake_config = MagicMock(name="config")
    fake_model = MagicMock(name="model")
    fake_tokenizer = MagicMock(name="tokenizer")
    fake_pipe = MagicMock(name="pipe")

    with (
        patch(
            "guardrails_ai.detect_jailbreak.resources._load_sanitized_config",
            return_value=fake_config,
        ) as mock_sanitize,
        patch(
            "guardrails_ai.detect_jailbreak.resources.AutoModelForSequenceClassification.from_pretrained",
            return_value=fake_model,
        ) as mock_model,
        patch(
            "guardrails_ai.detect_jailbreak.resources.AutoTokenizer.from_pretrained",
            return_value=fake_tokenizer,
        ) as mock_tokenizer,
        patch(
            "guardrails_ai.detect_jailbreak.resources.pipeline",
            return_value=fake_pipe,
        ) as mock_pipeline,
    ):
        result = load_text_classification_pipeline(
            "zhx123/ftrobertallm", max_length=512
        )

    mock_sanitize.assert_called_once_with("zhx123/ftrobertallm")
    mock_model.assert_called_once_with("zhx123/ftrobertallm", config=fake_config)
    mock_tokenizer.assert_called_once_with("zhx123/ftrobertallm", config=fake_config)
    mock_pipeline.assert_called_once_with(
        "text-classification",
        model=fake_model,
        tokenizer=fake_tokenizer,
        max_length=512,
    )
    assert result is fake_pipe
