import pytest
from guardrails import Guard
from guardrails_ai.african_compliance import AfricanCompliance

# ── Guard instances ───────────────────────────────────────────────────────────

guard_all = Guard().use(AfricanCompliance, on_fail="exception")
guard_sensitive = Guard().use(AfricanCompliance, checks=["sensitive_data"], on_fail="exception")
guard_cbn = Guard().use(AfricanCompliance, checks=["cbn_threshold"], on_fail="exception")
guard_cbk = Guard().use(AfricanCompliance, checks=["cbk_threshold"], on_fail="exception")
guard_cross = Guard().use(AfricanCompliance, checks=["cross_border"], on_fail="exception")


# ── Pass cases ────────────────────────────────────────────────────────────────


def test_pass_clean_text():
    result = guard_all.parse("The transaction was processed successfully.")
    assert result.validation_passed is True


def test_pass_small_ngn_amount():
    result = guard_cbn.parse("Transfer of ₦50,000 completed.")
    assert result.validation_passed is True


def test_pass_small_kes_amount():
    result = guard_cbk.parse("Payment of KES 500,000 received.")
    assert result.validation_passed is True


def test_pass_transfer_to_adequate_country():
    result = guard_cross.parse("Syncing records to the UK office.")
    assert result.validation_passed is True


def test_pass_country_name_no_transfer_verb():
    result = guard_cross.parse("Our partner is based in China.")
    assert result.validation_passed is True


# ── Sensitive data ────────────────────────────────────────────────────────────


def test_fail_health_data_ndpa():
    with pytest.raises(Exception) as exc_info:
        guard_sensitive.parse("The customer's health record was retrieved.")
    assert "NDPA" in str(exc_info.value)


def test_fail_biometric_data():
    with pytest.raises(Exception) as exc_info:
        guard_sensitive.parse("Biometric verification was completed.")
    assert "NDPA" in str(exc_info.value)


def test_fail_criminal_record_popia():
    guard_popia = Guard().use(
        AfricanCompliance, checks=["sensitive_data"], jurisdictions=["POPIA"], on_fail="exception"
    )
    with pytest.raises(Exception) as exc_info:
        guard_popia.parse("Customer has a criminal record from 2019.")
    assert "POPIA" in str(exc_info.value)


def test_fail_ethnic_origin_kdpa():
    guard_kdpa = Guard().use(
        AfricanCompliance, checks=["sensitive_data"], jurisdictions=["KDPA"], on_fail="exception"
    )
    with pytest.raises(Exception) as exc_info:
        guard_kdpa.parse("Ethnic origin was recorded in the profile.")
    assert "KDPA" in str(exc_info.value)


def test_pass_criminal_record_ndpa_only():
    guard_ndpa = Guard().use(
        AfricanCompliance, checks=["sensitive_data"], jurisdictions=["NDPA"], on_fail="exception"
    )
    result = guard_ndpa.parse("Customer has a criminal record from 2019.")
    assert result.validation_passed is True


# ── CBN thresholds ────────────────────────────────────────────────────────────


def test_fail_cbn_ctr_threshold():
    with pytest.raises(Exception) as exc_info:
        guard_cbn.parse("Transfer of ₦10,000,000 initiated.")
    assert "CBN" in str(exc_info.value)
    assert "CTR" in str(exc_info.value)


def test_fail_cbn_structuring_threshold():
    with pytest.raises(Exception) as exc_info:
        guard_cbn.parse("Amount: NGN 5,500,000 flagged.")
    assert "CBN" in str(exc_info.value)
    assert "structuring" in str(exc_info.value)


def test_fail_cbn_text_naira():
    with pytest.raises(Exception) as exc_info:
        guard_cbn.parse("The customer transferred 12000000 naira.")
    assert "CBN" in str(exc_info.value)


def test_pass_below_cbn_threshold():
    result = guard_cbn.parse("Approved transfer of NGN 4,999,999.")
    assert result.validation_passed is True


# ── CBK thresholds ────────────────────────────────────────────────────────────


def test_fail_cbk_ctr_threshold():
    with pytest.raises(Exception) as exc_info:
        guard_cbk.parse("Customer transferred KES 5,000,000.")
    assert "CBK" in str(exc_info.value)
    assert "CTR" in str(exc_info.value)


def test_fail_cbk_suspicious_threshold():
    with pytest.raises(Exception) as exc_info:
        guard_cbk.parse("Payment of KSh 2,000,000 received.")
    assert "CBK" in str(exc_info.value)


def test_pass_below_cbk_threshold():
    result = guard_cbk.parse("KES 800,000 withdrawn.")
    assert result.validation_passed is True


# ── Cross-border ──────────────────────────────────────────────────────────────


def test_fail_transfer_to_china():
    with pytest.raises(Exception) as exc_info:
        guard_cross.parse("Syncing customer records to China.")
    assert "NDPA" in str(exc_info.value)
    assert "adequacy" in str(exc_info.value)


def test_fail_export_to_russia():
    with pytest.raises(Exception) as exc_info:
        guard_cross.parse("Exporting data to Russia for analysis.")
    assert "NDPA" in str(exc_info.value)


# ── Multiple violations ───────────────────────────────────────────────────────


def test_fail_multiple_violations():
    text = (
        "Transferring health record of customer to China. "
        "Transaction amount: NGN 15,000,000."
    )
    with pytest.raises(Exception) as exc_info:
        guard_all.parse(text)
    error = str(exc_info.value)
    assert "NDPA" in error
    assert "CBN" in error


# ── Check filter ──────────────────────────────────────────────────────────────


def test_check_filter_ignores_disabled():
    guard_no_cbn = Guard().use(
        AfricanCompliance,
        checks=["sensitive_data", "cross_border"],
        on_fail="exception",
    )
    result = guard_no_cbn.parse("Transfer of NGN 20,000,000 approved.")
    assert result.validation_passed is True
