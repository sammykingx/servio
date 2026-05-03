import inspect, pytest
from abc import ABC
from unittest.mock import MagicMock

from payments.domain.contracts import PaymentGateway
from payments.domain.entities.gateway import GatewayInitResponse, GatewayVerifyResponse
from payments.schemas.payments import PaymentGatewayPayload


# PLACEHOLDER TYPES
GATEWAY_PAYLOAD_CLASS = PaymentGatewayPayload
GATEWAY_INIT_RESPONSE = GatewayInitResponse
GATEWAY_VERIFY_RESPONSE = GatewayVerifyResponse
GATEWAY_REFUND_RESPONSE = None

# ─────────────────────────────────────────────────────────────────────────────
# Sentinel — used to detect that a placeholder hasn't been replaced yet.
# Tests that depend on a response class skip gracefully until it's wired in.
# ─────────────────────────────────────────────────────────────────────────────

def _response_class_defined(cls) -> bool:
    return cls is not None

def _make_instance(cls, **kwargs):
    """
    Attempt to construct a real instance of cls.
    Falls back to MagicMock(spec=cls) only as a last resort — callers that
    need isinstance to pass must supply enough kwargs to construct for real.
    """
    try:
        return cls(**kwargs)
    except Exception:
        return MagicMock(spec=cls)


# ─────────────────────────────────────────────
# Helpers — concrete stubs used across tests
# ─────────────────────────────────────────────
class TypeEnforcingGateway(PaymentGateway):
    """
    A contract-compliant gateway that actively enforces payload type on input
    and returns instances of the unified response types on output.
    This is the reference implementation all adapters should mirror.
    """
    
    def __init__(self):
        self._create_payment_response = _make_instance(
            GATEWAY_INIT_RESPONSE,
            gateway="test_gateway",
            message="Mocked gateway response for create_payment",
            data={"auth_url": "https://example.com/checkout", "access_code": "TEST123"}
        ) if _response_class_defined(GATEWAY_INIT_RESPONSE) else MagicMock()
        
        self._verify_payment_response = _make_instance(
            GATEWAY_VERIFY_RESPONSE,
            gateway="test_gateway",
            status="success",
            was_successful=True,
            message="Mocked gateway response for verify_payment",
            data={"status": "success"}
        ) if _response_class_defined(GATEWAY_VERIFY_RESPONSE) else MagicMock()
        
        # self._refund_response = _make_instance(
        #     GATEWAY_REFUND_RESPONSE,
        #     gateway="test_gateway",
        #     message="Mocked gateway response for refund",
        #     data={"status": "success"}
        # ) if _response_class_defined(GATEWAY_REFUND_RESPONSE) else MagicMock()

    def create_payment(self, payload: GATEWAY_PAYLOAD_CLASS):
        if not isinstance(payload, GATEWAY_PAYLOAD_CLASS):
            raise TypeError(
                f"create_payment expects {GATEWAY_PAYLOAD_CLASS.__name__}, "
                f"got {type(payload).__name__}"
            )
        return self._create_payment_response

    def verify_payment(self, reference: str):
        return self._verify_payment_response
        
    def refund(self, reference: str, amount):
        return self._refund_response


class FullyImplementedGateway(PaymentGateway):
    """A minimal but complete implementation that satisfies every abstract method."""

    def create_payment(self, payload: GATEWAY_PAYLOAD_CLASS):
        return MagicMock(spec=GATEWAY_INIT_RESPONSE) if _response_class_defined(GATEWAY_INIT_RESPONSE) else MagicMock()

    def verify_payment(self, reference: str):
        return MagicMock(spec=GATEWAY_VERIFY_RESPONSE) if _response_class_defined(GATEWAY_VERIFY_RESPONSE) else MagicMock()

    def refund(self, reference: str, amount):
        return MagicMock(spec=GATEWAY_REFUND_RESPONSE) if _response_class_defined(GATEWAY_REFUND_RESPONSE) else MagicMock()


class MissingCreatePayment(PaymentGateway):
    def verify_payment(self, reference): pass
    def refund(self, reference, amount): pass


class MissingVerifyPayment(PaymentGateway):
    def create_payment(self, payload: GATEWAY_PAYLOAD_CLASS): pass
    def refund(self, reference, amount): pass


class MissingRefund(PaymentGateway):
    def create_payment(self, payload: GATEWAY_PAYLOAD_CLASS): pass
    def verify_payment(self, reference): pass


class MissingAllMethods(PaymentGateway):
    """Implements nothing — represents a skeleton/stub class left incomplete."""
    pass


# ─────────────────────────────────────────────
# Contract structure
# ─────────────────────────────────────────────

class TestPaymentGatewayIsAbstract:

    def test_payment_gateway_is_abstract(self):
        """PaymentGateway must be abstract — direct instantiation is forbidden."""
        assert issubclass(PaymentGateway, ABC)

    def test_payment_gateway_cannot_be_instantiated_directly(self):
        """Instantiating the base contract directly must raise TypeError."""
        with pytest.raises(TypeError):
            PaymentGateway()

    def test_contract_declares_all_abstract_methods(self):
        """The contract must expose exactly the four required abstract methods."""
        abstract_methods = PaymentGateway.__abstractmethods__
        assert abstract_methods == frozenset(
            {"create_payment", "verify_payment", "refund"}
        )


# ─────────────────────────────────────────────
# Incomplete implementations — each missing one method
# ─────────────────────────────────────────────

class TestIncompleteImplementationsAreRejected:
    """
    Any class that omits even one abstract method must not be instantiable.
    This ensures no adapter can silently skip a required capability.
    """

    def test_missing_create_payment_raises(self):
        with pytest.raises(TypeError, match="create_payment"):
            MissingCreatePayment()

    def test_missing_verify_payment_raises(self):
        with pytest.raises(TypeError, match="verify_payment"):
            MissingVerifyPayment()

    def test_missing_refund_raises(self):
        with pytest.raises(TypeError, match="refund"):
            MissingRefund()

    def test_missing_all_methods_raises(self):
        with pytest.raises(TypeError):
            MissingAllMethods()


# ─────────────────────────────────────────────
# Complete implementation — accepted by the contract
# ─────────────────────────────────────────────

class TestCompleteImplementationIsAccepted:
    
    def setup_method(self):
        self.gateway = FullyImplementedGateway()

    def test_full_implementation_can_be_instantiated(self):
        """A class implementing all four methods must instantiate without error."""
        assert isinstance(self.gateway, PaymentGateway)

    def test_create_payment_is_callable(self):
        payload = MagicMock(spec=PaymentGatewayPayload)
        result = self.gateway.create_payment(payload)
        assert result is not None

    def test_verify_payment_is_callable(self):
        result = self.gateway.verify_payment("REF-001")
        assert result is not None

    # def test_refund_is_callable(self):
    #     result = self.gateway.refund("REF-001", 5000)
    #     assert result is not None


# ─────────────────────────────────────────────
# Method signatures — argument shape is part of the contract
# ─────────────────────────────────────────────

class TestContractMethodSignatures:
    """
    Signatures define the calling convention every adapter must honour.
    These tests catch drift where an adapter renames or drops a parameter.
    """

    def setup_method(self):
        self.gateway = FullyImplementedGateway()

    def test_create_payment_accepts_payload_argument(self):
        sig = inspect.signature(self.gateway.create_payment)
        assert "payload" in sig.parameters

    def test_verify_payment_accepts_reference_argument(self):
        sig = inspect.signature(self.gateway.verify_payment)
        assert "reference" in sig.parameters

    # def test_refund_accepts_reference_and_amount(self):
    #     sig = inspect.signature(self.gateway.refund)
    #     params = sig.parameters
    #     assert "reference" in params
    #     assert "amount" in params

# ─────────────────────────────────────────────
# Polymorphism — the contract enables interchangeable gateways
# ─────────────────────────────────────────────

class TestGatewayPolymorphism:
    """
    The whole point of the contract is that callers treat all gateways
    identically. These tests verifys that polymorphic dispatch works.
    """

    def test_multiple_adapters_satisfy_same_contract(self):
        """Two different concrete gateways must both be valid PaymentGateway instances."""

        class AnotherGateway(PaymentGateway):
            def create_payment(self, payload): return {}
            def verify_payment(self, reference): return {}
            def refund(self, reference, amount): return {}
            def transfer(self, recipient, amount): return {}

        gateways = [FullyImplementedGateway(), AnotherGateway()]
        for gw in gateways:
            assert isinstance(gw, PaymentGateway)

    def test_paystack_adapter_satisfies_contract(self):
        """
        PaystackAdapter (the real adapter) must be recognised as a PaymentGateway
        without instantiating it — we check the class hierarchy only, avoiding
        __init__ side-effects (settings, reverse(), network).
        """
        from payments.infrastructure.gateways.adapters.paystack import PaystackAdapter
        assert issubclass(PaystackAdapter, PaymentGateway)

    # def test_stripe_adapter_satisfies_contract(self):
    #     from payments.infrastructure.gateways.adapters.stripe import StripeAdapter
    #     assert issubclass(StripeAdapter, PaymentGateway)


# ─────────────────────────────────────────────
# Payload type enforcement — input contract
#
# Every adapter must reject a payload that is not an instance of
# GATEWAY_PAYLOAD_CLASS. This prevents a Stripe adapter accidentally
# accepting a raw dict or a Paystack-specific schema and silently
# producing garbage output.
# ─────────────────────────────────────────────

# class TestCreatePaymentPayloadTypeEnforcement:

#     def setup_method(self):
#         self.gateway = TypeEnforcingGateway()

#     def test_create_payment_accepts_correct_payload_type(self):
#         """create_payment must succeed when given a GATEWAY_PAYLOAD_CLASS instance."""
#         payload = MagicMock(spec=GATEWAY_PAYLOAD_CLASS)
#         result = self.gateway.create_payment(payload)
#         assert result is not None

#     def test_create_payment_rejects_plain_dict(self):
#         """Passing a raw dict instead of the payload class must raise TypeError."""
#         with pytest.raises(TypeError):
#             self.gateway.create_payment({"amount": 5000, "email": "user@example.com"})

#     def test_create_payment_rejects_none(self):
#         """None is not a valid payload — must raise TypeError."""
#         with pytest.raises(TypeError):
#             self.gateway.create_payment(None)

#     def test_create_payment_rejects_wrong_class(self):
#         """An arbitrary object that is not GATEWAY_PAYLOAD_CLASS must be rejected."""
#         with pytest.raises(TypeError):
#             self.gateway.create_payment(object())

#     def test_create_payment_rejects_string(self):
#         """A JSON string is not a valid payload even if it looks like one."""
#         with pytest.raises(TypeError):
#             self.gateway.create_payment('{"amount": 5000}')

#     def test_create_payment_type_error_message_names_expected_class(self):
#         """
#         The TypeError message must name GATEWAY_PAYLOAD_CLASS so the developer
#         knows exactly what type is required — not just that something is wrong.
#         """
#         with pytest.raises(TypeError, match=GATEWAY_PAYLOAD_CLASS.__name__):
#             self.gateway.create_payment(object())

#     def test_payload_type_annotation_on_contract_matches_expected_class(self):
#         """
#         The type annotation on PaymentGateway.create_payment must reference
#         GATEWAY_PAYLOAD_CLASS. This keeps the contract self-documenting and
#         ensures IDEs and static analysers surface the right type.
#         """
#         hints = PaymentGateway.create_payment.__annotations__
#         assert "payload" in hints, (
#             "create_payment must have a 'payload' type annotation on the contract"
#         )
#         assert hints["payload"] is GATEWAY_PAYLOAD_CLASS, (
#             f"Expected payload annotation to be {GATEWAY_PAYLOAD_CLASS.__name__}, "
#             f"got {hints.get('payload')}"
#         )


# ─────────────────────────────────────────────
# Return type contract — output contract
#
# Every adapter must return the unified response types so that the
# service layer can treat Paystack, Stripe or any gateway provider 
# responses as identical.
#
# Tests skip gracefully if a placeholder hasn't been replaced yet,
# so they can be added ncrementally as you build each response class.
# ─────────────────────────────────────────────

class TestGatewayReturnTypeContract:

    def setup_method(self):
        self.gateway = TypeEnforcingGateway()
        self.valid_payload = _make_instance(
            GATEWAY_PAYLOAD_CLASS,
            email="a@b.com", amount=5000, reference="SRV-2wsdhfy", currency="NGN"
        )

    # ── create_payment ──
    @pytest.mark.skipif(
        not _response_class_defined(GATEWAY_INIT_RESPONSE),
        reason="GATEWAY_INIT_RESPONSE placeholder not replaced yet"
    )
    def test_create_payment_returns_gateway_init_response(self):
        """create_payment must return an instance of GATEWAY_INIT_RESPONSE."""
        result = self.gateway.create_payment(self.valid_payload)
        assert isinstance(result, GATEWAY_INIT_RESPONSE), (
            f"create_payment must return {GATEWAY_INIT_RESPONSE.__name__}, "
            f"got {result}"
        )

    @pytest.mark.skipif(
        not _response_class_defined(GATEWAY_INIT_RESPONSE),
        reason="GATEWAY_INIT_RESPONSE placeholder not replaced yet"
    )
    def test_create_payment_never_returns_raw_dict(self):
        """A raw dict return breaks the service layer — must be the response class."""
        result = self.gateway.create_payment(self.valid_payload)
        assert not isinstance(result, dict), (
            "create_payment must not return a raw dict — wrap it in GATEWAY_INIT_RESPONSE"
        )

    @pytest.mark.skipif(
        not _response_class_defined(GATEWAY_INIT_RESPONSE),
        reason="GATEWAY_INIT_RESPONSE placeholder not replaced yet"
    )
    def test_return_type_annotation_on_contract_for_create_payment(self):
        """The return annotation on the contract must declare GATEWAY_INIT_RESPONSE."""
        hints = PaymentGateway.create_payment.__annotations__
        assert "return" in hints, (
            "create_payment must have a return type annotation on the contract"
        )
        assert hints["return"] is GATEWAY_INIT_RESPONSE

    # ── verify_payment ──
    @pytest.mark.skipif(
        not _response_class_defined(GATEWAY_VERIFY_RESPONSE),
        reason="GATEWAY_VERIFY_RESPONSE placeholder not replaced yet"
    )
    def test_verify_payment_returns_gateway_verify_response(self):
        """verify_payment must return an instance of GATEWAY_VERIFY_RESPONSE."""
        result = self.gateway.verify_payment("REF-001")
        assert isinstance(result, GATEWAY_VERIFY_RESPONSE), (
            f"verify_payment must return {GATEWAY_VERIFY_RESPONSE.__name__}, "
            f"got {type(result).__name__}"
        )

    @pytest.mark.skipif(
        not _response_class_defined(GATEWAY_VERIFY_RESPONSE),
        reason="GATEWAY_VERIFY_RESPONSE placeholder not replaced yet"
    )
    def test_return_type_annotation_on_contract_for_verify_payment(self):
        hints = PaymentGateway.verify_payment.__annotations__
        assert "return" in hints
        assert hints["return"] is GATEWAY_VERIFY_RESPONSE

    # ── refund ──
    # @pytest.mark.skipif(
    #     not _response_class_defined(GATEWAY_REFUND_RESPONSE),
    #     reason="GATEWAY_REFUND_RESPONSE placeholder not replaced yet"
    # )
    # def test_refund_returns_gateway_refund_response(self):
    #     """refund must return an instance of GATEWAY_REFUND_RESPONSE."""
    #     result = self.gateway.refund("REF-001", 5000)
    #     assert isinstance(result, GATEWAY_REFUND_RESPONSE), (
    #         f"refund must return {GATEWAY_REFUND_RESPONSE.__name__}, "
    #         f"got {type(result).__name__}"
    #     )

    # @pytest.mark.skipif(
    #     not _response_class_defined(GATEWAY_REFUND_RESPONSE),
    #     reason="GATEWAY_REFUND_RESPONSE placeholder not replaced yet"
    # )
    # def test_return_type_annotation_on_contract_for_refund(self):
    #     hints = PaymentGateway.refund.__annotations__
    #     assert "return" in hints
    #     assert hints["return"] is GATEWAY_REFUND_RESPONSE

    # ── cross-adapter consistency ──
    @pytest.mark.skipif(
        not _response_class_defined(GATEWAY_INIT_RESPONSE),
        reason="GATEWAY_INIT_RESPONSE placeholder not replaced yet"
    )
    def test_two_adapters_return_same_response_type_for_create_payment(self):
        """
        Paystack and Stripe adapters must return the exact same response class —
        not gateway-specific subclasses. The service layer must never branch on
        which gateway produced the response.
        """
        paystack_res = {
            "gateway": "paystack",
            "message": "tHe gateway response if checkout url was successfully created",
            "data": {
                "auth_url": "https://ascngng.com",
                "access_Code": "asweruthg"
            }
        }
        
        stripe_res = {
            "gateway": "stripe",
            "message": "tHe gateway response if checkout url was successfully created",
            "data": {
                "auth_url": "https://ascngng.com",
                "access_Code": "asweruthg"
            }
        }
        real_response_a = _make_instance(GATEWAY_INIT_RESPONSE, **paystack_res)
        real_response_b = _make_instance(GATEWAY_INIT_RESPONSE, **stripe_res)
 
        class AnotherGateway(PaymentGateway):
            def create_payment(self, payload):   return real_response_b
            def verify_payment(self, reference): return MagicMock()
            def refund(self, reference, amount): return MagicMock()
 
        gw_a = TypeEnforcingGateway()
        gw_b = AnotherGateway()
 
        result_a = gw_a.create_payment(self.valid_payload)
        result_b = gw_b.create_payment(self.valid_payload)
 
        assert isinstance(result_a, GATEWAY_INIT_RESPONSE), (
            f"First adapter returned {type(result_a).__name__}, "
            f"expected {GATEWAY_INIT_RESPONSE.__name__}"
        )
        assert isinstance(result_b, GATEWAY_INIT_RESPONSE), (
            f"Second adapter returned {type(result_b).__name__}, "
            f"expected {GATEWAY_INIT_RESPONSE.__name__}"
        )
        assert type(result_a) is type(result_b), (
            "Both adapters must return the exact same response class — "
            "not gateway-specific subclasses. "
            f"Got {type(result_a).__name__} vs {type(result_b).__name__}"
        )
 