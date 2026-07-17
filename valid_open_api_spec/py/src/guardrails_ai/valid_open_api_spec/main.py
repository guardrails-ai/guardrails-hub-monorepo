import json
from string import Template
import yaml
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, jsonschema as jsonschema_ref
from typing import Callable, Dict, List, Optional, Union

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

from .schemas import open_api_spec_schema


@register_validator(
    name="guardrails/valid_open_api_spec", data_type=["string", "object"]
)
class ValidOpenApiSpec(Validator):
    """Validates that a value is a valid OpenAPI Specification.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/valid_open_api_spec`  |
    | Supported data types          | `string`, `object`                |
    | Programmatic fix              | None                              |
    """  # noqa

    _openapi_registry: Registry
    _openapi_spec_validator: Draft202012Validator

    def __init__(
        self,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail)
        self._openapi_registry = Registry().with_resources(
            [
                (
                    "urn:open-api-spec",
                    jsonschema_ref.DRAFT202012.create_resource(open_api_spec_schema),
                )
            ]
        )

        self._openapi_spec_validator = Draft202012Validator(
            {
                "$ref": "urn:open-api-spec",
            },
            registry=self._openapi_registry,
        )

    def _to_json(self, value: Union[str, Dict]):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                try:
                    return yaml.safe_load(value)
                except Exception:
                    return None
        return value

    def validate(self, value: Union[str, Dict], metadata: Dict) -> ValidationResult:
        potential_spec = self._to_json(value)

        fields: Dict[str, List[str]] = {}
        error: ValidationError
        for error in self._openapi_spec_validator.iter_errors(potential_spec):
            fields[error.json_path] = fields.get(error.json_path, [])
            fields[error.json_path].append(error.message)

        if fields:
            error_message = Template(
                """Value is not a valid OpenAPI Specification.
The following fields are invalid:
${fields}
            """
            )
            return FailResult(
                error_message=error_message.safe_substitute(
                    {"fields": json.dumps(fields, indent=2)}
                )
            )

        return PassResult()
