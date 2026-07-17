import asyncio
import concurrent.futures

from guardrails import AsyncGuard, Guard, OnFailAction
from guardrails_ai.secrets_present import SecretsPresent
import pytest


@pytest.mark.parametrize(
    "value",
    [
        """
        def hello_world():
            print("Hello, World!")
            var_a = "This is not a secret"
            var_b = "This is also not a secret"
        """,
        """
        import guardrails as gd
        import openai
        print("Hello from Guardrails!")
        """,
    ],
)
def test_happy_path(value):
    """Test happy path."""
    guard = Guard().use(SecretsPresent(on_fail=OnFailAction.EXCEPTION))
    response = guard.validate(value)
    assert response.validation_passed is True


@pytest.mark.parametrize(
    "value",
    [
        """
        def hello_world():
            print("Hello, World!")
            usd_api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
            user_password = "password123"
        """,
        """
        import guardrails as gd
        import openai
        print("Hello from Guardrails!")
        var_a = "This is not a secret"
        pwd = "lx123"
        """,
    ],
)
def test_fail_path(value):
    """Test fail path."""
    guard = Guard().use(SecretsPresent(on_fail=OnFailAction.EXCEPTION))
    with pytest.raises(Exception):
        guard.validate(value)


def test_concurrent_validation():
    """Multiple SecretsPresent instances should not interfere with each other."""

    def validate(text):
        guard = Guard().use(SecretsPresent(on_fail=OnFailAction.NOOP))
        return guard.validate(text)

    clean_inputs = [
        "no secrets here\n",
        "also clean text\n",
        "nothing to see\n",
    ]
    secret_inputs = [
        'api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"\n',  # gitleaks:allow
    ]
    inputs = clean_inputs + secret_inputs

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(validate, text): text for text in inputs}
        results = {text: f.result() for f, text in futures.items()}

    assert len(results) == 4
    for text in clean_inputs:
        assert results[text].validation_passed is True
    for text in secret_inputs:
        assert results[text].validation_passed is False


@pytest.mark.asyncio
async def test_async_concurrent_validation():
    """Multiple async SecretsPresent validations should not interfere with each other."""

    async def validate(text):
        guard = AsyncGuard().use(SecretsPresent(on_fail=OnFailAction.NOOP))
        return await guard.validate(text)

    clean_inputs = [
        "no secrets here\n",
        "also clean text\n",
        "nothing to see\n",
    ]
    secret_inputs = [
        'api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"\n',  # gitleaks:allow
    ]
    inputs = clean_inputs + secret_inputs

    results = await asyncio.gather(*[validate(text) for text in inputs])

    assert len(results) == 4
    for i, text in enumerate(clean_inputs):
        assert results[i].validation_passed is True
    for i, text in enumerate(secret_inputs, start=len(clean_inputs)):
        assert results[i].validation_passed is False
