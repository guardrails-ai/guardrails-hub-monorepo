import pytest
from guardrails import Guard
from guardrails_ai.african_pii import AfricanPii

# ── Guard instances ──────────────────────────────────────────────────────────

guard_all = Guard().use(AfricanPii, on_fail="exception")
guard_fix = Guard().use(AfricanPii, on_fail="fix")
guard_ng_only = Guard().use(AfricanPii, jurisdictions=["NG"], on_fail="exception")


# ── Pass cases ───────────────────────────────────────────────────────────────


def test_pass_clean_text():
    result = guard_all.parse("The customer completed their KYC verification.")
    assert result.validation_passed is True


def test_pass_unrelated_numbers():
    result = guard_all.parse("The invoice total is 12345678 and reference is ORDER-99.")
    assert result.validation_passed is True


def test_pass_jurisdiction_filter_ignores_other():
    result = guard_ng_only.parse("Customer Ghana Card: GHA-123456789-1")
    assert result.validation_passed is True


# ── Nigeria ───────────────────────────────────────────────────────────────────


def test_fail_bvn():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Customer BVN: 12345678901")
    assert "BVN" in str(exc_info.value)
    assert "NG" in str(exc_info.value)


def test_fail_nin():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("NIN 98765432101 was verified.")
    assert "NIN" in str(exc_info.value)


def test_fail_cac():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Company registration: RC1234567")
    assert "CAC_RC_NUMBER" in str(exc_info.value)


def test_fail_ng_phone():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Call the customer on +2348012345678")
    assert "PHONE_NG" in str(exc_info.value)


# ── Kenya ─────────────────────────────────────────────────────────────────────


def test_fail_kra_pin():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("KRA PIN: A123456789Z for taxpayer")
    assert "KRA_PIN" in str(exc_info.value)


def test_fail_ke_phone():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Contact: +254712345678")
    assert "PHONE_KE" in str(exc_info.value)


# ── South Africa ──────────────────────────────────────────────────────────────


def test_fail_sa_id():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("South African ID: 9202204720082")
    assert "NATIONAL_ID_ZA" in str(exc_info.value)


def test_fail_za_phone():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Phone: +27821234567")
    assert "PHONE_ZA" in str(exc_info.value)


# ── Ghana ─────────────────────────────────────────────────────────────────────


def test_fail_ghana_card():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Ghana Card number: GHA-123456789-1")
    assert "GHANA_CARD" in str(exc_info.value)


def test_fail_gh_phone():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Reach me at +233201234567")
    assert "PHONE_GH" in str(exc_info.value)


# ── Rwanda ────────────────────────────────────────────────────────────────────


def test_fail_rw_national_id():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("National ID 1199880012345678 registered.")
    assert "NATIONAL_ID_RW" in str(exc_info.value)


def test_fail_rw_phone():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Kigali contact: +250781234567")
    assert "PHONE_RW" in str(exc_info.value)


# ── Egypt ─────────────────────────────────────────────────────────────────────


def test_fail_eg_national_id():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("National ID 29001011234567 on file.")
    assert "NATIONAL_ID_EG" in str(exc_info.value)


def test_fail_eg_phone():
    with pytest.raises(Exception) as exc_info:
        guard_all.parse("Cairo number: +201012345678")
    assert "PHONE_EG" in str(exc_info.value)


# ── Redaction (fix mode) ──────────────────────────────────────────────────────


def test_fix_redacts_bvn():
    result = guard_fix.parse("BVN: 12345678901 approved")
    assert "[BVN]" in result.validated_output
    assert "12345678901" not in result.validated_output


def test_fix_redacts_ghana_card():
    result = guard_fix.parse("Card GHA-123456789-1 issued.")
    assert "[GHANA_CARD]" in result.validated_output
    assert "GHA-123456789-1" not in result.validated_output
