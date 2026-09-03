from backend.reconciliation import reconcile_record


def make_order(amount=1000):
    return {
        "order_id": "ORD_TEST",
        "customer_name": "Test Customer",
        "order_amount": amount,
        "order_date": "2026-09-03",
        "order_status": "CONFIRMED"
    }


def make_payment(amount=1000, status="SUCCESS"):
    return {
        "payment_id": "PAY_TEST",
        "order_id": "ORD_TEST",
        "payment_amount": amount,
        "payment_date": "2026-09-03",
        "payment_status": status,
        "payment_method": "CARD"
    }


def make_settlement(amount=1000, status="SETTLED"):
    return {
        "settlement_id": "SET_TEST",
        "payment_id": "PAY_TEST",
        "settlement_amount": amount,
        "settlement_date": "2026-09-03",
        "settlement_status": status
    }


def test_matched_transaction():

    result = reconcile_record(
        make_order(),
        make_payment(),
        make_settlement()
    )

    assert result["status"] == "MATCHED"
    assert result["severity"] == "LOW"
    assert result["reason_code"] == "FULL_MATCH"
    assert result["discrepancy_amount"] == 0


def test_pending_payment():

    result = reconcile_record(
        make_order(),
        make_payment(status="PENDING"),
        make_settlement(status="PENDING")
    )

    assert result["status"] == "PENDING"
    assert result["severity"] == "MEDIUM"
    assert result["reason_code"] == "SETTLEMENT_NOT_COMPLETED"


def test_amount_mismatch():

    result = reconcile_record(
        make_order(1000),
        make_payment(900),
        make_settlement(900)
    )

    assert result["status"] == "MISMATCH"
    assert result["severity"] == "HIGH"
    assert result["reason_code"] == "PAYMENT_AMOUNT_MISMATCH"
    assert result["discrepancy_amount"] == 100