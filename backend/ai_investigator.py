def investigate_case(reconciliation):

    status = reconciliation["status"]
    reason_code = reconciliation["reason_code"]

    if status == "MATCHED":
        return {
            "ai_decision": "AUTO_RESOLVE",
            "confidence": 0.99,
            "explanation": "Order, payment, and settlement amounts match and the transaction is successfully settled."
        }

    if reason_code == "SETTLEMENT_AMOUNT_MISMATCH":
        discrepancy = reconciliation["discrepancy_amount"]

        return {
            "ai_decision": "REVIEW_REQUIRED",
            "confidence": 0.97,
            "explanation": (
                f"The order and payment amounts differ from the settlement "
                f"amount by ₹{discrepancy}. This may indicate a settlement "
                f"deduction, partial settlement, or reconciliation error."
            )
        }

    if reason_code == "SETTLEMENT_NOT_COMPLETED":
        return {
            "ai_decision": "FOLLOW_UP",
            "confidence": 0.95,
            "explanation": (
                "The payment was not successfully settled. "
                "The transaction should remain in the exception queue "
                "until settlement is completed or the failure is investigated."
            )
        }

    return {
        "ai_decision": "MANUAL_REVIEW",
        "confidence": 0.80,
        "explanation": "The transaction contains an unusual reconciliation condition and requires manual investigation."
    }