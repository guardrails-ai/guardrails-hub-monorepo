# guardrails-ai-bert-toxic

Validates that the input string does not contain toxic language based on a BERT model.

## Installation

```bash
pip install guardrails-ai-bert-toxic
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.bert_toxic.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.bert_toxic import BertToxic

guard = Guard().use(BertToxic)
```

## License

MIT — © Guardrails AI.
