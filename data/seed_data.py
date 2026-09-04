from datetime import datetime, timedelta
from sqlalchemy import text

from backend.database import engine


def seed_data():

    with engine.begin() as db:

        base_date = datetime(2026, 9, 1)

        for i in range(11, 61):

            order_id = f"ORD{i:03d}"
            payment_id = f"PAY{i:03d}"
            settlement_id = f"SET{i:03d}"

            order_amount = 1000 + (i * 100)

            # Create different transaction scenarios
            if i % 10 == 0:
                # Amount mismatch
                payment_amount = order_amount - 100
                settlement_amount = payment_amount - 50

                payment_status = "SUCCESS"
                settlement_status = "SETTLED"

            elif i % 7 == 0:
                # Pending transaction
                payment_amount = order_amount
                settlement_amount = order_amount

                payment_status = "PENDING"
                settlement_status = "PENDING"

            else:
                # Fully matched transaction
                payment_amount = order_amount
                settlement_amount = order_amount

                payment_status = "SUCCESS"
                settlement_status = "SETTLED"

            order_date = base_date + timedelta(days=i % 5)

            db.execute(
                text("""
                    INSERT INTO orders (
                        order_id,
                        customer_name,
                        order_amount,
                        order_date,
                        order_status
                    )
                    VALUES (
                        :order_id,
                        :customer_name,
                        :order_amount,
                        :order_date,
                        :order_status
                    )
                    ON CONFLICT (order_id) DO NOTHING;
                """),
                {
                    "order_id": order_id,
                    "customer_name": f"Customer {i}",
                    "order_amount": order_amount,
                    "order_date": order_date,
                    "order_status": "CONFIRMED"
                }
            )

            db.execute(
                text("""
                    INSERT INTO payments (
                        payment_id,
                        order_id,
                        payment_amount,
                        payment_date,
                        payment_status,
                        payment_method
                    )
                    VALUES (
                        :payment_id,
                        :order_id,
                        :payment_amount,
                        :payment_date,
                        :payment_status,
                        :payment_method
                    )
                    ON CONFLICT (payment_id) DO NOTHING;
                """),
                {
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "payment_amount": payment_amount,
                    "payment_date": order_date,
                    "payment_status": payment_status,
                    "payment_method": "CARD"
                }
            )

            db.execute(
                text("""
                    INSERT INTO settlements (
                        settlement_id,
                        payment_id,
                        settlement_amount,
                        settlement_date,
                        settlement_status
                    )
                    VALUES (
                        :settlement_id,
                        :payment_id,
                        :settlement_amount,
                        :settlement_date,
                        :settlement_status
                    )
                    ON CONFLICT (settlement_id) DO NOTHING;
                """),
                {
                    "settlement_id": settlement_id,
                    "payment_id": payment_id,
                    "settlement_amount": settlement_amount,
                    "settlement_date": order_date + timedelta(days=1),
                    "settlement_status": settlement_status
                }
            )

    print("Synthetic data seeding completed.")
    print("Transactions available: ORD001 to ORD060")


if __name__ == "__main__":
    seed_data()