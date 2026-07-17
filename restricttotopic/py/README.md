# guardrails-ai-restrict-to-topic

Checks that a text's topic is within a set of valid topics and, optionally, that
it avoids a set of invalid topics. By default it runs a local zero-shot
classifier (`facebook/bart-large-mnli`) and falls back to an LLM when the
classifier is not confident.

Registered as `tryolabs/restricttotopic`.

## Installation

```bash
pip install guardrails-ai-restrict-to-topic
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.restricttotopic import RestrictToTopic

guard = Guard().use(
    RestrictToTopic(
        valid_topics=["sports", "politics"],
        invalid_topics=["music"],
        disable_llm=True,  # zero-shot classifier only (no OpenAI key needed)
        on_fail="exception",
    )
)

guard.validate("The Chiefs won the Super Bowl.")  # passes
```

The default ensemble mode also uses an LLM fallback and requires `OPENAI_API_KEY`.

## License

Apache-2.0. Originally authored by Tryolabs.
