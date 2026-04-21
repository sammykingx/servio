# Registry to resolve which payment gateway to use.

from payments.infrastructure.gateways.adapters.paystack import PaystackAdapter
# from payments.infrastructure.gateways.adapter.stripe import StripeAdapter


GATEWAYS = {
    "paystack": PaystackAdapter,
    # "stripe": StripeAdapter,
}
