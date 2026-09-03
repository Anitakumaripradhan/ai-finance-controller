import json
from backend.reconciliation import reconcile_record
from backend.ai_investigator import investigate_case
from fastapi import FastAPI
from sqlalchemy import text
from backend.database import engine

app = FastAPI(
    title="ReconAI",
    description="AI Finance Controller",
    version="1.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to ReconAI API"
    }

@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }

@app.get("/orders")
def get_orders():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    order_id,
                    customer_name,
                    order_amount,
                    order_date,
                    order_status
                FROM orders
                ORDER BY order_date;
            """)
        )

        orders = [dict(row) for row in result.mappings().all()]

    return {
        "count": len(orders),
        "orders": orders
    }
    
@app.get("/payments")
def get_payments():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    payment_id,
                    order_id,
                    payment_amount,
                    payment_date,
                    payment_status,
                    payment_method
                FROM payments
                ORDER BY payment_date;
            """)
        )

        payments = [dict(row) for row in result.mappings().all()]

    return {
        "count": len(payments),
        "payments": payments
    }
    
@app.get("/settlements")
def get_settlements():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    s.settlement_id,
                    s.payment_id,
                    p.order_id,
                    s.settlement_amount,
                    s.settlement_date,
                    s.settlement_status
                FROM settlements s
                JOIN payments p
                    ON s.payment_id = p.payment_id
                ORDER BY s.settlement_date;
            """)
        )

        settlements = [dict(row) for row in result.mappings().all()]

    return {
        "count": len(settlements),
        "settlements": settlements
    }
    
@app.get("/reconcile")
def reconcile_all():

    with engine.connect() as db:

        orders = db.execute(
            text("""
                SELECT
                    order_id,
                    customer_name,
                    order_amount,
                    order_date,
                    order_status
                FROM orders
                ORDER BY order_date;
            """)
        ).mappings().all()

        payments = db.execute(
            text("""
                SELECT
                    payment_id,
                    order_id,
                    payment_amount,
                    payment_date,
                    payment_status,
                    payment_method
                FROM payments
                ORDER BY payment_date;
            """)
        ).mappings().all()

        settlements = db.execute(
            text("""
                SELECT
                    settlement_id,
                    payment_id,
                    settlement_amount,
                    settlement_date,
                    settlement_status
                FROM settlements
                ORDER BY settlement_date;
            """)
        ).mappings().all()

    payment_map = {
        payment["order_id"]: payment
        for payment in payments
    }

    settlement_map = {
        settlement["payment_id"]: settlement
        for settlement in settlements
    }

    results = []

    for order in orders:

        payment = payment_map.get(order["order_id"])

        if not payment:
            results.append({
                "order_id": order["order_id"],
                "status": "MISMATCH",
                "issues": ["Payment record not found"]
            })
            continue

        settlement = settlement_map.get(
            payment["payment_id"]
        )

        if not settlement:
            results.append({
                "order_id": order["order_id"],
                "payment_id": payment["payment_id"],
                "status": "MISMATCH",
                "issues": ["Settlement record not found"]
            })
            continue

        result = reconcile_record(
            order,
            payment,
            settlement
        )

        ai_result = investigate_case(result)

        result.update(ai_result)

        results.append(result)

    return {
        "count": len(results),
        "reconciliation": results
    }
    
@app.get("/exceptions")
def get_exceptions():

    reconciliation_data = reconcile_all()

    exceptions = [
        item
        for item in reconciliation_data["reconciliation"]
        if item["status"] != "MATCHED"
    ]

    return {
        "count": len(exceptions),
        "exceptions": exceptions
    }
    
@app.get("/audit")
def get_audit_logs():

    reconciliation_data = reconcile_all()

    reconciliation_map = {
        item["order_id"]: item
        for item in reconciliation_data["reconciliation"]
    }

    with engine.begin() as db:

        exception_rows = db.execute(
            text("""
                SELECT
                    exception_id,
                    reconciliation_id,
                    order_id,
                    exception_type,
                    description,
                    difference_amount,
                    severity,
                    status
                FROM exceptions
                ORDER BY exception_id;
            """)
        ).mappings().all()

        for exception in exception_rows:

            item = reconciliation_map.get(
                exception["order_id"]
            )

            if not item:
                continue

            action = "AI_INVESTIGATION"

            existing = db.execute(
                text("""
                    SELECT audit_id
                    FROM audit_logs
                    WHERE exception_id = :exception_id
                      AND action = :action
                    LIMIT 1;
                """),
                {
                    "exception_id": exception["exception_id"],
                    "action": action
                }
            ).first()

            if existing:
                continue

            details = json.dumps({
                "order_id": exception["order_id"],
                "exception_type": exception["exception_type"],
                "status": item["status"],
                "severity": item["severity"],
                "reason_code": item["reason_code"],
                "discrepancy_amount": item["discrepancy_amount"],
                "ai_decision": item["ai_decision"],
                "confidence": item["confidence"],
                "explanation": item["explanation"]
            })

            db.execute(
                text("""
                    INSERT INTO audit_logs (
                        exception_id,
                        action,
                        actor,
                        details
                    )
                    VALUES (
                        :exception_id,
                        :action,
                        :actor,
                        :details
                    );
                """),
                {
                    "exception_id": exception["exception_id"],
                    "action": action,
                    "actor": "ReconAI",
                    "details": details
                }
            )

        result = db.execute(
            text("""
                SELECT
                    audit_id,
                    exception_id,
                    action,
                    actor,
                    details,
                    created_at
                FROM audit_logs
                ORDER BY created_at DESC, audit_id DESC;
            """)
        )

        logs = [
            dict(row)
            for row in result.mappings().all()
        ]

    return {
        "count": len(logs),
        "audit_logs": logs
    }