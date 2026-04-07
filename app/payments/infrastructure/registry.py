# Registry to resolve which payment gateway to use.

# payments/registry.py

from payments.infrastructure.gateways.paystack.adapter import PaystackAdapter
# from payments.infrastructure.gateways.stripe.adapter import StripeAdapter


GATEWAYS = {
    "paystack": PaystackAdapter,
    # "stripe": StripeAdapter,
}
