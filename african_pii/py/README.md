# guardrails-ai-african-pii

Detects African-specific personally identifiable information (PII) in text.

Generic PII validators have no awareness of African identity formats. This validator fills that gap with pattern-based detection aligned to each country's official format specifications, covering **16 entity types across 6 jurisdictions**.

## Installation

```bash
pip install guardrails-ai-african-pii
```

## Covered entities

| Entity | Jurisdiction | Format |
|---|---|---|
| `BVN` | Nigeria (NG) | Labelled 11-digit Bank Verification Number |
| `NIN` | Nigeria (NG) | Labelled 11-digit National Identity Number |
| `CAC_RC_NUMBER` | Nigeria (NG) | `RC` + 4–7 digits (corporate registration) |
| `PHONE_NG` | Nigeria (NG) | `+234` / `0[789]` prefix |
| `KRA_PIN` | Kenya (KE) | Letter + 9 digits + letter (e.g. `A001234567Z`) |
| `NATIONAL_ID_KE` | Kenya (KE) | Labelled 7–8 digit national ID |
| `PHONE_KE` | Kenya (KE) | `+254` / `0[71]` prefix |
| `NATIONAL_ID_ZA` | South Africa (ZA) | Labelled 13-digit SA ID number |
| `SARS_TAX_REF` | South Africa (ZA) | Labelled 10-digit SARS tax reference |
| `PHONE_ZA` | South Africa (ZA) | `+27` / `0` prefix |
| `GHANA_CARD` | Ghana (GH) | `GHA-XXXXXXXXX-X` format |
| `PHONE_GH` | Ghana (GH) | `+233` / `0[25]` prefix |
| `NATIONAL_ID_RW` | Rwanda (RW) | Labelled 16-digit national ID |
| `PHONE_RW` | Rwanda (RW) | `+250` / `07` prefix |
| `NATIONAL_ID_EG` | Egypt (EG) | Labelled 14-digit national ID (Latin + Arabic label) |
| `PHONE_EG` | Egypt (EG) | `+20` / `01[0-5]` prefix |

## Regulatory alignment

- **NDPA 2023** — Nigeria Data Protection Act, §30 sensitive personal data
- **KDPA 2019** — Kenya Data Protection Act, §43 sensitive data
- **POPIA** — South Africa Protection of Personal Information Act, §26
- **Ghana DPA 2012** — Ghana Data Protection Act
- **Rwanda Law No. 058/2021** — personal data protection
- **Egypt DPL No. 151/2020** — Egypt Data Protection Law

## Usage

```python
from guardrails import Guard
from guardrails_ai.african_pii import AfricanPii

# Detect all African PII (raises on match)
guard = Guard().use(AfricanPii, on_fail="exception")
guard.parse("Customer BVN: 12345678901")
# → raises ValidationError: African PII detected — BVN (NG)

# Auto-redact detected PII
guard_fix = Guard().use(AfricanPii, on_fail="fix")
result = guard_fix.parse("BVN: 12345678901 approved")
print(result.validated_output)
# → "[BVN] approved"

# Scope to specific jurisdictions
guard_ng_ke = Guard().use(AfricanPii, jurisdictions=["NG", "KE"], on_fail="exception")

# Scope to specific entity types
guard_ids = Guard().use(AfricanPii, entities=["BVN", "GHANA_CARD", "KRA_PIN"], on_fail="exception")
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `entities` | `list[str] \| None` | `None` (all) | Entity types to detect |
| `jurisdictions` | `list[str] \| None` | `None` (all) | Country codes to check |
| `on_fail` | `str \| Callable` | — | Guardrails failure action |

When `on_fail="fix"`, detected PII is replaced with `[ENTITY_TYPE]` placeholders.

## License

MIT — © Guardrails AI.
