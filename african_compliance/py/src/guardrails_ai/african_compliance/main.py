from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Set

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

# ── Sensitive data keyword patterns ─────────────────────────────────────────
# Special-category data keywords under African data protection laws.
# NDPA §30, POPIA §26, KDPA §43, Ghana DPA §72.

_BASE_SENSITIVE = [
    r"\bhealth\s+(?:record|data|information|status)\b",
    r"\bmedical\s+(?:record|history|data|report)\b",
    r"\bbiometric\b",
    r"\bfingerprint\b",
    r"\bfacial\s+recognition\b",
    r"\bretinal\s+scan\b",
    r"\bgenetic\s+(?:data|information|profile)\b",
    r"\breligious\s+(?:belief|affiliation|view)\b",
    r"\bpolitical\s+(?:opinion|affiliation|view)\b",
    r"\btrade\s+union\b",
    r"\bsexual\s+orientation\b",
    r"\bchild(?:ren)?(?:'s)?\s+(?:data|information|record|profile)\b",
    r"\bjuvenile\s+(?:record|data)\b",
]

_POPIA_EXTRA = [
    r"\bcriminal\s+(?:record|offence|conviction|history)\b",
    r"\bprosecution\s+record\b",
]

_KDPA_EXTRA = [
    r"\bethnic\s+(?:origin|group|background)\b",
    r"\brace\b",
    r"\btribal\s+(?:affiliation|group)\b",
]

_SENSITIVE_PATTERNS: Dict[str, List[re.Pattern]] = {
    "NDPA": [re.compile(kw, re.IGNORECASE) for kw in _BASE_SENSITIVE],
    "POPIA": [re.compile(kw, re.IGNORECASE) for kw in _BASE_SENSITIVE + _POPIA_EXTRA],
    "KDPA": [re.compile(kw, re.IGNORECASE) for kw in _BASE_SENSITIVE + _KDPA_EXTRA],
    "GH_DPA": [re.compile(kw, re.IGNORECASE) for kw in _BASE_SENSITIVE],
    "RW_DPA": [re.compile(kw, re.IGNORECASE) for kw in _BASE_SENSITIVE],
}

# ── Transaction amount patterns ──────────────────────────────────────────────

# Matches: "NGN 5,000,000" / "₦5000000" / "5,000,000 NGN" / "5000000 naira"
_NGN_RE = re.compile(
    r"(?:NGN|₦|naira)\s*(\d[\d,]*(?:\.\d{1,2})?)\b"
    r"|"
    r"\b(\d[\d,]*(?:\.\d{1,2})?)\s*(?:NGN|₦|naira)\b",
    re.IGNORECASE,
)

# Matches: "KES 1,000,000" / "KSh 1000000" / "1,000,000 KES" / "shillings 1000000"
_KES_RE = re.compile(
    r"(?:KES|KSh|shillings?)\s*(\d[\d,]*(?:\.\d{1,2})?)\b"
    r"|"
    r"\b(\d[\d,]*(?:\.\d{1,2})?)\s*(?:KES|KSh|shillings?)\b",
    re.IGNORECASE,
)

# ── Cross-border adequacy ────────────────────────────────────────────────────
# Countries without adequacy determination under NDPA 2023 §43.

_INADEQUATE_COUNTRY_RE = re.compile(
    r"\b(?:china|CN|russia|RU|iran|north\s+korea|DPRK|belarus|myanmar|cuba|syria)\b",
    re.IGNORECASE,
)

_DATA_TRANSFER_RE = re.compile(
    r"\b(?:transfer|export|send|sync|replicate|upload|push)(?:ring|red|s|ed|ing)?\b",
    re.IGNORECASE,
)


def _parse_amount(raw: str) -> float:
    return float(raw.replace(",", ""))


@register_validator(name="guardrails/african_compliance", data_type="string")
class AfricanCompliance(Validator):
    """Validates LLM outputs for African financial and data protection compliance.

    Performs four independent checks on the output string:

    1. **sensitive_data** — Flags special-category data keywords under
       NDPA 2023 (Nigeria), POPIA (South Africa), KDPA 2019 (Kenya),
       Ghana DPA 2012, Rwanda Law 058/2021.

    2. **cbn_threshold** — Flags Nigerian Naira (NGN/₦) amounts that
       cross CBN AML/CFT reporting thresholds:
       - ≥ ₦5,000,000 → structuring risk, compliance review required
       - ≥ ₦10,000,000 → mandatory Currency Transaction Report (CTR)

    3. **cbk_threshold** — Flags Kenyan Shilling (KES) amounts that
       cross CBK AML/CFT thresholds:
       - ≥ KES 1,000,000 → suspicious transaction, enhanced due diligence
       - ≥ KES 5,000,000 → mandatory CTR

    4. **cross_border** — Flags data transfer language directed at
       countries without NDPA 2023 adequacy determination.

    **Key Properties**

    | Property                      | Description                              |
    | ----------------------------- | ---------------------------------------- |
    | Name for `format` attribute   | `guardrails/african_compliance`          |
    | Supported data types          | `string`                                 |
    | Programmatic fix              | None — raises FailResult with violations |

    Args:
        checks (list, optional): Checks to run. None = all.
            Options: "sensitive_data", "cbn_threshold", "cbk_threshold", "cross_border"
        jurisdictions (list, optional): Regulatory frameworks for sensitive_data check.
            Options: "NDPA", "POPIA", "KDPA", "GH_DPA", "RW_DPA". None = all.
        on_fail (Callable, optional): Failure action.
    """  # noqa: E501

    _ALL_CHECKS: Set[str] = {"sensitive_data", "cbn_threshold", "cbk_threshold", "cross_border"}

    def __init__(
        self,
        checks: Optional[List[str]] = None,
        jurisdictions: Optional[List[str]] = None,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(checks=checks, jurisdictions=jurisdictions, on_fail=on_fail)
        self.checks: Set[str] = set(checks) if checks else self._ALL_CHECKS
        self.jurisdictions: Set[str] = (
            set(jurisdictions) if jurisdictions else set(_SENSITIVE_PATTERNS.keys())
        )

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Runs enabled compliance checks and returns FailResult if any violations found."""
        if not isinstance(value, str):
            return PassResult()

        violations: List[str] = []

        if "sensitive_data" in self.checks:
            violations.extend(self._check_sensitive_data(value))
        if "cbn_threshold" in self.checks:
            violations.extend(self._check_cbn_threshold(value))
        if "cbk_threshold" in self.checks:
            violations.extend(self._check_cbk_threshold(value))
        if "cross_border" in self.checks:
            violations.extend(self._check_cross_border(value))

        if not violations:
            return PassResult()

        return FailResult(
            error_message=(
                "African compliance violations detected:\n"
                + "\n".join(f"  • {v}" for v in violations)
            )
        )

    # ── Checks ───────────────────────────────────────────────────────────────

    def _check_sensitive_data(self, text: str) -> List[str]:
        violations: List[str] = []
        for jurisdiction in self.jurisdictions:
            patterns = _SENSITIVE_PATTERNS.get(jurisdiction, [])
            matched = [p.pattern for p in patterns if p.search(text)]
            if matched:
                short = matched[:2]
                more = f" (+{len(matched) - 2} more)" if len(matched) > 2 else ""
                violations.append(
                    f"[{jurisdiction}] Special-category data detected "
                    f"({', '.join(short)}{more}). "
                    "Explicit consent and DPIA required before processing."
                )
        return violations

    def _check_cbn_threshold(self, text: str) -> List[str]:
        violations: List[str] = []
        for m in _NGN_RE.finditer(text):
            raw = m.group(1) or m.group(2)
            if not raw:
                continue
            amount = _parse_amount(raw)
            if amount >= 10_000_000:
                violations.append(
                    f"[CBN] Amount ₦{amount:,.0f} exceeds mandatory CTR threshold "
                    f"(₦10,000,000). Currency Transaction Report required under "
                    f"CBN AML/CFT/CPF Regulations 2023."
                )
            elif amount >= 5_000_000:
                violations.append(
                    f"[CBN] Amount ₦{amount:,.0f} exceeds structuring threshold "
                    f"(₦5,000,000). Flag for compliance officer review."
                )
        return violations

    def _check_cbk_threshold(self, text: str) -> List[str]:
        violations: List[str] = []
        for m in _KES_RE.finditer(text):
            raw = m.group(1) or m.group(2)
            if not raw:
                continue
            amount = _parse_amount(raw)
            if amount >= 5_000_000:
                violations.append(
                    f"[CBK] Amount KES {amount:,.0f} exceeds mandatory CTR threshold "
                    f"(KES 5,000,000). Report required under CBK AML/CFT Guidelines."
                )
            elif amount >= 1_000_000:
                violations.append(
                    f"[CBK] Amount KES {amount:,.0f} exceeds suspicious transaction "
                    f"threshold (KES 1,000,000). Enhanced due diligence required."
                )
        return violations

    def _check_cross_border(self, text: str) -> List[str]:
        if _DATA_TRANSFER_RE.search(text) and _INADEQUATE_COUNTRY_RE.search(text):
            country_match = _INADEQUATE_COUNTRY_RE.search(text)
            country = country_match.group(0) if country_match else "flagged country"
            return [
                f"[NDPA] Cross-border data transfer to '{country}' detected. "
                "This country lacks an adequacy determination under NDPA 2023 §43. "
                "Transfer prohibited without Standard Contractual Clauses or NITDA approval."
            ]
        return []
