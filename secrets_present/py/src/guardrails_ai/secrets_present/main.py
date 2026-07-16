import os
import tempfile
import threading
import warnings
from typing import Any, Callable, Dict, List, Tuple, Union

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

# detect_secrets' `settings.default_settings()` mutates process-global state and
# is not thread-safe, so serialize scans across threads.
_DETECT_SECRETS_LOCK = threading.Lock()


@register_validator(name="guardrails/secrets_present", data_type="string")
class SecretsPresent(Validator):
    """Validates whether the generated code snippet contains any secrets.

    **Key Properties**
    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/secrets_present`      |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |

    Args:
        None

    This validator uses the `detect-secrets` library to check whether the generated code
    snippet contains any secrets. If any secrets are detected, the validator fails and
    returns the generated code snippet with the secrets replaced with asterisks.
    Else the validator returns the generated code snippet.

    Following are some caveats:
        - Multiple secrets on the same line may not be caught. e.g.
            - Minified code
            - One-line lists/dictionaries
            - Multi-variable assignments
        - Multi-line secrets may not be caught. e.g.
            - RSA/SSH keys

    Example:
        ```py

        guard = Guard.for_string(validators=[
            DetectSecrets(on_fail="fix")
        ])
        guard.parse(
            llm_output=code_snippet,
        )
        ```
    """

    def __init__(self, on_fail: Union[Callable[..., Any], None] = None, **kwargs):
        super().__init__(on_fail, **kwargs)

        self.mask = "********"

    def get_unique_secrets(self, value: str) -> Tuple[Dict[str, Any], List[str]]:
        """Get unique secrets from the value.

        Args:
            value (str): The generated code snippet.

        Returns:
            unique_secrets (Dict[str, Any]): A dictionary of unique secrets and their
                line numbers.
            lines (List[str]): The lines of the generated code snippet.
        """
        # Use a unique temp file per call to avoid race conditions when
        # multiple SecretsPresent instances run concurrently.
        fd, temp_path = tempfile.mkstemp(suffix=".txt", prefix="guardrails_secrets_")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(value)

            try:
                from detect_secrets import settings
                from detect_secrets.core.secrets_collection import SecretsCollection

                secrets = SecretsCollection()

                with _DETECT_SECRETS_LOCK:
                    with settings.default_settings():
                        secrets.scan_file(temp_path)
            except ImportError:
                raise ValueError(
                    "You must install detect-secrets in order to "
                    "use the DetectSecrets validator."
                )

            # Get unique secrets from these secrets
            unique_secrets = {}
            for secret in secrets:
                _, potential_secret = secret
                actual_secret = potential_secret.secret_value
                line_number = potential_secret.line_number
                if actual_secret not in unique_secrets:
                    unique_secrets[actual_secret] = [line_number]
                else:
                    if line_number not in unique_secrets[actual_secret]:
                        unique_secrets[actual_secret].append(line_number)

            with open(temp_path, "r") as f:
                lines = f.readlines()
        finally:
            # Always clean up, even if an exception occurred above.
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        return unique_secrets, lines

    def get_modified_value(
        self, unique_secrets: Dict[str, Any], lines: List[str]
    ) -> str:
        """Replace the secrets on the lines with asterisks.

        Args:
            unique_secrets (Dict[str, Any]): A dictionary of unique secrets and their
                line numbers.
            lines (List[str]): The lines of the generated code snippet.

        Returns:
            modified_value (str): The generated code snippet with secrets replaced with
                asterisks.
        """
        # Replace the secrets on the lines with asterisks
        for secret, line_numbers in unique_secrets.items():
            for line_number in line_numbers:
                lines[line_number - 1] = lines[line_number - 1].replace(
                    secret, self.mask
                )

        # Convert lines to a multiline string
        modified_value = "".join(lines)
        return modified_value

    def validate(self, value: str, metadata: Dict[str, Any]) -> ValidationResult:
        # Check if value is a multiline string
        if "\n" not in value:
            # Raise warning if value is not a multiline string
            warnings.warn(
                "The DetectSecrets validator works best with "
                "multiline code snippets. "
                "Refer validator docs for more details."
            )

            # Add a newline to value
            value += "\n"

        # Get unique secrets from the value
        unique_secrets, lines = self.get_unique_secrets(value)

        if unique_secrets:
            # Replace the secrets on the lines with asterisks
            modified_value = self.get_modified_value(unique_secrets, lines)

            return FailResult(
                error_message=(
                    "The following secrets were detected in your response:\n"
                    + "\n".join(unique_secrets.keys())
                ),
                fix_value=modified_value,
            )
        return PassResult()
