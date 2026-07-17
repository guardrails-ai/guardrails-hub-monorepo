import re
from typing import Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="cartesia/quotes_price", data_type="string")
class QuotesPrice(Validator):
    """Validates that the generated text contains a price quote in a given currency.

    **Key Properties**

    | Property                     | Description                   |
    |------------------------------|-------------------------------|
    | Name for `format` attribute  | `cartesia/quotes_price`       |
    | Supported data types         | `string`                      |
    | Programmatic fix             | N/A                           |
    """

    DEFAULT_CURRENCY = "USD"
    SYMBOLS = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "AUD": "A$",
        "CAD": "C$",
        "CNY": "¥",
        "NZD": "NZ$",
    }

    def __init__(self, on_fail: Optional[Callable] = None, **kwargs):
        super().__init__(on_fail, **kwargs)

    def quotes_price(
        self,
        value: str,
        currency: str,
    ) -> bool:
        """Check if the generated text contains a price quote in the given currency.

        Args:
            value (str): The generated text.

        Returns:
            bool: Whether the generated text has a price quote.
        """
        symbol = self.SYMBOLS[currency]
        # Create a regex pattern to match the currency symbol and a number
        pattern = rf"{re.escape(symbol)}\s*\d+(?:\.\d+)?"

        # Check if the pattern is present in the generated text
        return bool(re.search(pattern, value))

    def _unpack_metadata(self, metadata: Dict[str, str]) -> str:
        """Unpacks the metadata and returns the relevant fields."""
        currency = metadata.get("currency", self.DEFAULT_CURRENCY)
        assert currency in self.SYMBOLS, f"Currency {currency} not supported."
        return currency

    def validate(self, value: str, metadata: Dict[str, str] = {}) -> ValidationResult:
        """Validation function for the `cartesia/quotes_price` validator."""

        # Get the currency from the metadata
        currency = self._unpack_metadata(metadata)

        # Check if the generated text contains a price quote in the given currency
        if self.quotes_price(value, currency):
            return FailResult(
                metadata=metadata,
                error_message=f"The generated text contains a price quote in {currency}.",
            )
        return PassResult()
