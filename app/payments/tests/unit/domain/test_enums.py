import pytest
from payments.domain.enums import (
    RegisteredPaymentProvider,
    PaymentType,
    PaymentPurpose,
    PaymentStatus,
    EscrowStatus,
    PaymentPhase,
)

    
class TestPaymentEnumContracts:
    """
    Ensures the string values of enums remain unchanged to preserve 
    idempotency logic and database integrity.
    """

    @pytest.mark.parametrize("member, expected_value", [
        (PaymentType.ONE_TIME, "one_time"),
        (PaymentType.SERVICE, "service"),
    ])
    def test_payment_type_values(self, member, expected_value):
        """Verify PaymentType string values stay constant."""
        assert member.value == expected_value

    @pytest.mark.parametrize("member, expected_value", [
        (PaymentPurpose.ACTIVATION_FEE, "activation_fee"),
        (PaymentPurpose.SERVICE_PAYMENT, "service_payment"),
        (PaymentPurpose.WALLET_FUNDING, "wallet_funding"),
    ])
    def test_payment_purpose_values(self, member, expected_value):
        """Verify PaymentPurpose string values stay constant for idempotency."""
        assert member.value == expected_value
        
    @pytest.mark.parametrize("gateway, provider", [
        (RegisteredPaymentProvider.PAYSTACK, "paystack"),
        (RegisteredPaymentProvider.STRIPE, "stripe")
    ])
    def test_payment_gateway_values(self, gateway, provider):
        """Ensures the gateway strings are not accidentally changed"""
        assert gateway.value == provider
        
    @pytest.mark.parametrize("member, expected_string", [
        (PaymentStatus.ABANDONED, "abandoned"),
        (PaymentStatus.INITIATED, "initiated"),
        (PaymentStatus.PENDING, "pending"),
        (PaymentStatus.SUCCESS, "success"),
        (PaymentStatus.FAILED, "failed"),
        (PaymentStatus.CANCELLED, "cancelled"),
        (PaymentStatus.UNDERPAID, "underpaid"),
        (PaymentStatus.EXPIRED, "expired"),
        (PaymentStatus.REFUNDED, "refunded"),
    ])
    def test_payment_status_value_integrity(self, member, expected_string):
        """
        Critical: Ensures the string values of PaymentStatus remain unchanged.
        Changes to these strings will break database lookups and state transitions.
        """
        assert member.value == expected_string

    @pytest.mark.parametrize("enum_cls", [
        EscrowStatus,
        PaymentStatus,
        PaymentType,
        PaymentPurpose,
        RegisteredPaymentProvider,
    ])
    def test_enum_choices_integrity(self, enum_cls):
        """Ensure the .choices() method generates the correct Django format."""
        assert enum_cls.choices() == [
            (item.value, item.name) for item in enum_cls
        ]
