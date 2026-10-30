# guardrails-ai-drex-policy

Checks text, or text with images, against a Drex noul or score question and fails when the answer crosses a threshold.

## Overview

| Developed by | Nace.AI |
| --- | --- |
| Date of development | Oct 29, 2026 |
| Validator type | Moderation, policy |
| Blog |  |
| License | MIT |
| Input/Output | Input, Output |

## Description

### Intended Use

`DrexPolicy` asks [Drex](https://console.nace.ai/docs) one question about a string and fails when the answer crosses a threshold you set. Use it for checks such as PII present, off-topic, toxicity level, jailbreak attempt, or competitor mention.

The question is a `nace_sdk.Noul` (probability of a yes answer) or a `nace_sdk.Score` (expected index over criteria you list). Drex returns the probability. You choose the threshold with `fail_at`, preferably from labeled examples from your application.

- Noul: fails when P(yes) is at or above `fail_at`. With `fail_when="no"`, fails when P(yes) is below `fail_at`.
- Score: fails when the score is at or above `fail_at`. With `fail_when="below"`, fails when the score is below `fail_at`.

The Drex answer is in the result metadata on pass and on fail.

### Models

The default model is `drex-v2.0`. Text-only checks can use any Drex model id, which is sent unchanged. `drex-latest` is sent as `drex-latest`. It is not `drex-max`.

To check images with the text, pass `model="drex-max"` and put the images in `metadata["images"]`. Each image is a URL or a data URL (PNG, JPEG, or WebP). `drex-max` accepts at most 8 images. If images are present and the model is not `drex-max`, or there are more than 8 images, the validator raises `DrexPolicyError` before it calls Drex. It does not drop the images.

### Requirements

* Dependencies:
	- guardrails-ai>=0.4.0
	- nace-sdk>=0.6.2

* Access keys:
	- `NACE_API_KEY`: a key from [console.nace.ai](https://console.nace.ai)
	- `NACE_BASE_URL` (optional): defaults to `https://console.nace.ai`

When the validator builds its own client, each HTTP attempt times out after 60 seconds, the total retry budget is 180 seconds, and requests carry `X-Nace-Client: drex-policy/0.1.0`.

## Installation

```bash
pip install guardrails-ai-drex-policy
```

## Usage Examples

### Validating string output via Python

```python
from guardrails import Guard
from guardrails_ai.drex_policy import DrexPolicy
from nace_sdk import Noul

guard = Guard().use(
    DrexPolicy(
        question=Noul(instructions="Does the text contain a personal phone number or email address?"),
        fail_at=0.5,
        on_fail="exception",
    )
)

guard.validate("Our office opens at 9am.")  # Validator passes
guard.validate("Call me on +1 415 555 0100.")  # Validator fails
```

### Checking text with images

```python
from guardrails import Guard
from guardrails_ai.drex_policy import DrexPolicy
from nace_sdk import Score

guard = Guard().use(
    DrexPolicy(
        question=Score(
            instructions="How unsafe is this listing for a general audience?",
            criteria=["safe", "borderline", "unsafe"],
        ),
        fail_at=1.5,
        model="drex-max",
        on_fail="exception",
    )
)

guard.validate(
    "Vintage camera, works well.",
    metadata={"images": ["https://example.com/listing.jpg"]},
)
```

### Validating JSON output via Python

```python
from pydantic import BaseModel, Field
from guardrails import Guard
from guardrails_ai.drex_policy import DrexPolicy
from nace_sdk import Noul

off_topic = DrexPolicy(
    question=Noul(instructions="Is this reply about something other than our billing product?"),
    fail_at=0.5,
    on_fail="exception",
)


class Reply(BaseModel):
    answer: str = Field(validators=[off_topic])


guard = Guard.for_pydantic(output_class=Reply)
guard.parse('{"answer": "Your invoice is in Settings > Billing."}')
```

# API Reference

**`__init__(self, question, fail_at, fail_when=None, question_id="policy", model=None, client=None, on_fail=None)`**
<ul>
Initializes a new instance of the DrexPolicy class.

**Parameters**
- **`question`** *(nace_sdk.Noul | nace_sdk.Score)*: The question Drex answers about the value. If `instructions` is omitted, it stays `None` and is not sent.
- **`fail_at`** *(float)*: For a noul, a P(yes) threshold between 0 and 1. For a score, a finite expected-index threshold.
- **`fail_when`** *(str)*: `"yes"` (default) or `"no"` for a noul. `"at_or_above"` (default) or `"below"` for a score.
- **`question_id`** *(str)*: Key of the question in the Drex request and response. Default `"policy"`.
- **`model`** *(str)*: Drex model id. Default `drex-v2.0`. Images need `drex-max`.
- **`client`** *(nace_sdk.NaceClient)*: An existing client. If omitted, the validator builds one that reads `NACE_API_KEY` and `NACE_BASE_URL`.
- **`on_fail`** *(str, Callable)*: The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
</ul>
<br/>

**`validate(self, value, metadata) -> ValidationResult`**
<ul>
Asks Drex the question about `value` and compares the answer with `fail_at`. Do not call it directly. `guard.parse(...)` and `guard.validate(...)` call it.

If Drex cannot answer (a network error, an API error, or a response without the expected answer), the exception propagates. The validator does not turn it into a pass or a fail.

**Parameters**
- **`value`** *(str)*: The text to check.
- **`metadata`** *(dict)*: Optional.

    | Key | Type | Description | Default |
    | --- | --- | --- | --- |
    | `images` | list[str] | Image URLs or data URLs. Needs `model="drex-max"`; at most 8. | None |

**Result metadata**

| Key | Description |
| --- | --- |
| `drex_model` | Model id sent to Drex |
| `drex_question_id` | The `question_id` |
| `drex_answer` | The Drex answer, for example `{"type": "noul", "noul": 0.93}` |
</ul>

## License

MIT — © 2026 Nace.AI.

Scaffolding from [guardrails-ai/validator-template](https://github.com/guardrails-ai/validator-template) (Apache-2.0).
