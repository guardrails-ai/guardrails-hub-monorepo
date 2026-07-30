from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

# ── Pattern registry ────────────────────────────────────────────────────────
# Each entry: (compiled_re, entity_type, jurisdiction, capture_group)
# capture_group=0 → full match span; capture_group=1 → first group span

_PATTERNS: List[Tuple[re.Pattern, str, str, int]] = [
    # ── Nigeria ─────────────────────────────────────────────────────────────
    # BVN: 11-digit number, typically appears labelled in text
    (re.compile(r"(?i)\bBVN\b[\s:]*(\d{11})\b"), "BVN", "NG", 1),
    # NIN: 11-digit number, appears labelled
    (re.compile(r"(?i)\bNIN\b[\s:]*(\d{11})\b"), "NIN", "NG", 1),
    # CAC registration number: RC + 4–7 digits
    (re.compile(r"\bRC\s?\d{4,7}\b", re.IGNORECASE), "CAC_RC_NUMBER", "NG", 0),
    # Nigerian phone numbers (+234 or 0 + 7/8/9 prefix)
    (re.compile(r"(?<!\d)(?:\+234|0)(?:7|8|9)\d{9}(?!\d)"), "PHONE_NG", "NG", 0),
    # ── Kenya ────────────────────────────────────────────────────────────────
    # KRA PIN: distinctive — letter + 9 digits + letter (e.g. A001234567Z)
    (re.compile(r"\b[A-Z]\d{9}[A-Z]\b"), "KRA_PIN", "KE", 0),
    # Kenya National ID: 7–8 digits, labelled context
    (re.compile(r"(?i)\b(?:National\s+ID|ID\s+No\.?)\b[\s:]*(\d{7,8})\b"), "NATIONAL_ID_KE", "KE", 1),
    # Kenyan phone numbers (+254 or 0 + 7/1 prefix)
    (re.compile(r"(?<!\d)(?:\+254|0)(?:7|1)\d{8}(?!\d)"), "PHONE_KE", "KE", 0),
    # ── South Africa ────────────────────────────────────────────────────────
    # SA ID: 13 digits, labelled context (standalone too noisy)
    (re.compile(r"(?i)\b(?:SA\s+ID|ID\s+Number|South\s+African\s+ID)\b[\s:]*(\d{13})\b"), "NATIONAL_ID_ZA", "ZA", 1),
    # SARS tax reference: 10 digits, labelled
    (re.compile(r"(?i)\b(?:Tax\s+(?:Ref(?:erence)?|No\.?))\b[\s:]*(\d{10})\b"), "SARS_TAX_REF", "ZA", 1),
    # South African phone numbers (+27 or 0 prefix)
    (re.compile(r"(?<!\d)(?:\+27|0)\d{9}(?!\d)"), "PHONE_ZA", "ZA", 0),
    # ── Ghana ────────────────────────────────────────────────────────────────
    # Ghana Card: distinctive format GHA-XXXXXXXXX-X
    (re.compile(r"\bGHA-\d{9}-\d\b"), "GHANA_CARD", "GH", 0),
    # Ghanaian phone numbers (+233 or 0 + 2/5 prefix)
    (re.compile(r"(?<!\d)(?:\+233|0)(?:2|5)\d{8}(?!\d)"), "PHONE_GH", "GH", 0),
    # ── Rwanda ──────────────────────────────────────────────────────────────
    # Rwanda National ID: 16 digits starting with 1, labelled context
    (re.compile(r"(?i)\b(?:National\s+ID|NID)\b[\s:]*(\d{16})\b"), "NATIONAL_ID_RW", "RW", 1),
    # Rwandan phone numbers (+250 or 0 + 7 prefix)
    (re.compile(r"(?<!\d)(?:\+250|0)7\d{8}(?!\d)"), "PHONE_RW", "RW", 0),
    # ── Egypt ────────────────────────────────────────────────────────────────
    # Egypt National ID: 14 digits, labelled context (Latin + Arabic label)
    (re.compile(r"(?i)\b(?:National\s+ID|رقم\s+قومي)\b[\s:]*(\d{14})\b"), "NATIONAL_ID_EG", "EG", 1),
    # Egyptian phone numbers (+20 or 0 + 1 + 0–5 prefix)
    (re.compile(r"(?<!\d)(?:\+20|0)1[0-5]\d{8}(?!\d)"), "PHONE_EG", "EG", 0),
]


@dataclass
class PiiMatch:
    entity_type: str
    jurisdiction: str
    value: str
    start: int
    end: int


@register_validator(name="guardrails/african_pii", data_type="string")
class AfricanPii(Validator):
    """Detects African-specific personally identifiable information (PII).

    Generic PII validators (Presidio, spaCy NER) have no awareness of African
    identity formats. This validator fills that gap with pattern-based detection
    aligned to each country's official format specifications.

    Covers identity numbers, tax PINs, and phone formats for:
    Nigeria (NG), Kenya (KE), South Africa (ZA), Ghana (GH), Rwanda (RW), Egypt (EG).

    Aligns with:
    - Nigeria Data Protection Act 2023 (NDPA) — §30 sensitive personal data
    - Kenya Data Protection Act 2019 (KDPA) — §43 sensitive data
    - South Africa Protection of Personal Information Act (POPIA) — §26
    - Ghana Data Protection Act 2012
    - Rwanda Law No. 058/2021 on personal data protection
    - Egypt Data Protection Law No. 151/2020

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/african_pii`            |
    | Supported data types          | `string`                            |
    | Programmatic fix              | Redacts detected PII with `[TYPE]`  |

    Args:
        entities (list, optional): Entity types to detect. None = all.
            Example: ["BVN", "GHANA_CARD", "KRA_PIN"]
        jurisdictions (list, optional): Country codes to check. None = all.
            Example: ["NG", "KE", "ZA", "GH", "RW", "EG"]
        on_fail (Callable, optional): Failure action — "exception", "fix", etc.
    """  # noqa: E501

    def __init__(
        self,
        entities: Optional[List[str]] = None,
        jurisdictions: Optional[List[str]] = None,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(entities=entities, jurisdictions=jurisdictions, on_fail=on_fail)
        self.entities: Optional[Set[str]] = set(entities) if entities else None
        self.jurisdictions: Optional[Set[str]] = set(jurisdictions) if jurisdictions else None

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Scans the string for African PII and returns a FailResult if any is found."""
        if not isinstance(value, str):
            return PassResult()

        matches = self._find_pii(value)
        if not matches:
            return PassResult()

        detected = [f"{m.entity_type} ({m.jurisdiction})" for m in matches]
        return FailResult(
            error_message=(
                f"African PII detected — {', '.join(detected)}. "
                "This data must be handled in compliance with applicable data "
                "protection laws (NDPA 2023, POPIA, KDPA 2019, Ghana DPA 2012, "
                "Rwanda Law 058/2021, Egypt DPL 151/2020)."
            ),
            fix_value=self._redact(value, matches),
        )

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _find_pii(self, text: str) -> List[PiiMatch]:
        hits: List[PiiMatch] = []
        for pattern, entity_type, jurisdiction, group_idx in _PATTERNS:
            if self.jurisdictions and jurisdiction not in self.jurisdictions:
                continue
            if self.entities and entity_type not in self.entities:
                continue
            for m in pattern.finditer(text):
                start, end = m.span(group_idx) if group_idx else m.span(0)
                hits.append(
                    PiiMatch(
                        entity_type=entity_type,
                        jurisdiction=jurisdiction,
                        value=m.group(group_idx) if group_idx else m.group(0),
                        start=start,
                        end=end,
                    )
                )
        hits.sort(key=lambda x: x.start)
        return self._remove_overlaps(hits)

    def _remove_overlaps(self, matches: List[PiiMatch]) -> List[PiiMatch]:
        result: List[PiiMatch] = []
        last_end = -1
        for m in matches:
            if m.start >= last_end:
                result.append(m)
                last_end = m.end
        return result

    def _redact(self, text: str, matches: List[PiiMatch]) -> str:
        chars = list(text)
        for m in reversed(matches):
            chars[m.start : m.end] = list(f"[{m.entity_type}]")
        return "".join(chars)
