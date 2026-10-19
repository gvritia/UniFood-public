import random
from datetime import datetime


class PaymentStub:
    @staticmethod
    def process_payment(payment_data: dict) -> dict:
        """Simple sandbox payment stub for smoke/integration testing."""
        fake_card = payment_data.get("card_last4", "4242")
        payment_id = f"PAY-{datetime.now().strftime('%y%m%d')}-{random.randint(100000, 999999)}"
        amount = payment_data.get("total", 0)

        # Avoid symbols that may fail in cp1251 console encoding on Windows.
        print(
            f"[PAYMENT STUB] Payment success. ID: {payment_id}, card: ****{fake_card}, amount: {amount} RUB"
        )

        return {
            "payment_id": payment_id,
            "status": "success",
            "amount": amount,
            "card_last4": fake_card,
            "message": "Sandbox payment successful",
        }


payment_stub = PaymentStub()