from unittest.mock import MagicMock, patch

from guardrails_ai.detect_jailbreak.resources import get_text_classifier_pipeline

# zhx123/ftrobertallm (the default TEXT_CLASSIFIER_NAME) publishes id2label/
# label2id with integer values, e.g. {"0": 0, "1": 1}. huggingface_hub's strict
# dataclass validation on PretrainedConfig only accepts dict[int, str] or
# dict[str, str] for those fields, so AutoConfig.from_pretrained(model_name)
# raises StrictDataclassFieldValidationError before returning a config object
# to fix -- this is what get_config_dict() (a plain dict, unvalidated) plus a
# manual coercion step works around.
MALFORMED_CONFIG_DICT = {
    "model_type": "roberta",
    "id2label": {"0": 0, "1": 1},
    "label2id": {"0": 0, "1": 1},
}


def test_coerces_malformed_id2label_and_label2id():
    with (
        patch(
            "guardrails_ai.detect_jailbreak.resources.PretrainedConfig.get_config_dict",
            return_value=(dict(MALFORMED_CONFIG_DICT), {}),
        ),
        patch(
            "guardrails_ai.detect_jailbreak.resources.CONFIG_MAPPING",
            {
                "roberta": MagicMock(
                    from_dict=MagicMock(
                        side_effect=lambda d: MagicMock(id2label=d["id2label"])
                    )
                )
            },
        ),
        patch(
            "guardrails_ai.detect_jailbreak.resources.AutoModelForSequenceClassification.from_pretrained"
        ) as mock_model,
        patch(
            "guardrails_ai.detect_jailbreak.resources.AutoTokenizer.from_pretrained"
        ) as mock_tokenizer,
        patch("guardrails_ai.detect_jailbreak.resources.pipeline") as mock_pipeline,
    ):
        get_text_classifier_pipeline("zhx123/ftrobertallm")

        # The config actually built and passed to the model/tokenizer must have
        # string values, not the original malformed int values.
        built_config = mock_model.call_args.kwargs["config"]
        assert built_config.id2label == {"0": "0", "1": "1"}
        assert mock_tokenizer.call_args.kwargs["config"] is built_config

        # pipeline() must receive the already-constructed model/tokenizer
        # objects, not the model name string -- passing the name string is what
        # makes pipeline() re-derive (and re-fail on) the config internally.
        assert mock_pipeline.call_args.kwargs["model"] is mock_model.return_value
        assert (
            mock_pipeline.call_args.kwargs["tokenizer"] is mock_tokenizer.return_value
        )
        assert "zhx123/ftrobertallm" not in mock_pipeline.call_args.args
        assert "zhx123/ftrobertallm" not in mock_pipeline.call_args.kwargs.values()
