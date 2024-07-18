from yookassa import Payment
from yookassa.domain.exceptions.api_error import ApiError
from yookassa.payment import PaymentResponse


def create_payment(
    amount: float, return_url: str, description: str
) -> PaymentResponse | None:
    try:
        payment = Payment.create(
            {
                "amount": {"value": str(amount), "currency": "RUB"},
                "payment_method_data": {"type": "bank_card"},
                "confirmation": {"type": "redirect", "return_url": return_url},
                "description": description,
            }
        )
        return payment
    except ApiError:
        # e.response.json()
        return None
