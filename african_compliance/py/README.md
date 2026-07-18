# guardrails-ai-african-compliance

Validates LLM outputs for African financial and data protection compliance.

Performs four independent checks covering regulatory frameworks across Nigeria, Kenya, South Africa, Ghana, and Rwanda — with no external dependencies beyond `guardrails-ai`.

## Installation

```bash
pip install guardrails-ai-african-compliance
```

## Checks

| Check | What it flags |
|---|---|
| `sensitive_data` | Special-category data keywords (health, biometric, genetic, criminal records, etc.) under NDPA/POPIA/KDPA/GH_DPA/RW_DPA |
| `cbn_threshold` | Nigerian Naira amounts ≥ ₦5M (structuring) or ≥ ₦10M (mandatory CTR) under CBN AML/CFT Regulations 2023 |
| `cbk_threshold` | Kenyan Shilling amounts ≥ KES 1M (enhanced due diligence) or ≥ KES 5M (mandatory CTR) under CBK AML/CFT Guidelines |
| `cross_border` | Data transfer language targeting countries without NDPA 2023 §43 adequacy determination |

## Regulatory alignment

- **NDPA 2023** — Nigeria Data Protection Act, §30 (sensitive data), §43 (cross-border transfers)
- **POPIA** — South Africa Protection of Personal Information Act, §26
- **KDPA 2019** — Kenya Data Protection Act, §43
- **Ghana DPA 2012** — §72 sensitive data
- **Rwanda Law No. 058/2021** — personal data protection
- **CBN AML/CFT/CPF Regulations 2023** — Currency Transaction Report thresholds
- **CBK AML/CFT Guidelines** — suspicious transaction thresholds

## Usage

```python
from guardrails import Guard
from guardrails_ai.african_compliance import AfricanCompliance

# All checks enabled
guard = Guard().use(AfricanCompliance, on_fail="exception")
guard.parse("Transferring health record to China. NGN 15,000,000 disbursed.")
# → raises ValidationError listing all violations

# Scope to specific checks
guard_cbn = Guard().use(AfricanCompliance, checks=["cbn_threshold"], on_fail="exception")
guard_cbn.parse("Transfer of ₦10,000,000 initiated.")
# → raises: [CBN] Amount ₦10,000,000 exceeds mandatory CTR threshold

# Scope sensitive_data to specific jurisdictions
guard_popia = Guard().use(
    AfricanCompliance,
    checks=["sensitive_data"],
    jurisdictions=["POPIA"],
    on_fail="exception",
)
guard_popia.parse("Customer has a criminal record from 2019.")
# → raises: [POPIA] Special-category data detected
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `checks` | `list[str] \| None` | `None` (all) | Checks to run |
| `jurisdictions` | `list[str] \| None` | `None` (all) | Regulatory frameworks for `sensitive_data` |
| `on_fail` | `str \| Callable` | — | Guardrails failure action |

## License

MIT — © Guardrails AI.
