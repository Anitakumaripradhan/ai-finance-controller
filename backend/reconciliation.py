def reconcile_record(order, payment, settlement):
    """
    Reconcile one order, payment, and settlement record.
    """

    result = {
        "order_id": order["order_id"],
        "payment_id": payment["payment_id"],
        "settlement_id": settlement["settlement_id"],
        "status": "MATCHED",
        "severity": "LOW",
        "reason_code": "FULL_MATCH",
        "discrepancy_amount": 0,
        "issues": []
    }

    order_amount = order["order_amount"]
    payment_amount = payment["payment_amount"]
    settlement_amount = settlement["settlement_amount"]

    # -------------------------------------------------
    # 1. Check payment status
    # -------------------------------------------------

    if payment["payment_status"] != "SUCCESS":

        result["status"] = "PENDING"
        result["severity"] = "MEDIUM"
        result["reason_code"] = "PAYMENT_NOT_SUCCESSFUL"

        result["issues"].append(
            f"Payment status is {payment['payment_status']}"
        )


    # -------------------------------------------------
    # 2. Check Order vs Payment
    # -------------------------------------------------

    if order_amount != payment_amount:

        result["status"] = "MISMATCH"
        result["severity"] = "HIGH"
        result["reason_code"] = "PAYMENT_AMOUNT_MISMATCH"

        result["discrepancy_amount"] = float(
            abs(order_amount - payment_amount)
        )

        result["issues"].append(
            f"Order amount ({order_amount}) "
            f"!= Payment amount ({payment_amount})"
        )

    # -------------------------------------------------
    # 3. Check Payment vs Settlement
    # -------------------------------------------------

    if payment_amount != settlement_amount:

        result["status"] = "MISMATCH"
        result["severity"] = "HIGH"
        result["reason_code"] = "SETTLEMENT_AMOUNT_MISMATCH"

        settlement_difference = float(
            abs(payment_amount - settlement_amount)
        )

        order_settlement_difference = float(
            abs(order_amount - settlement_amount)
        )

        result["discrepancy_amount"] = max(
            result["discrepancy_amount"],
            settlement_difference,
            order_settlement_difference
        )

        result["issues"].append(
            f"Payment amount ({payment_amount}) "
            f"!= Settlement amount ({settlement_amount})"
        )


    # -------------------------------------------------
    # 4. Check Settlement Status
    # -------------------------------------------------

    if settlement["settlement_status"] != "SETTLED":

        result["status"] = "PENDING"
        result["severity"] = "MEDIUM"
        result["reason_code"] = "SETTLEMENT_NOT_COMPLETED"

        result["issues"].append(
            f"Settlement status is "
            f"{settlement['settlement_status']}"
        )


    return result