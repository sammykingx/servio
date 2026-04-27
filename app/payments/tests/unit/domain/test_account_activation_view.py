"""
Unit tests for account activation view & template.

Covers:
    - AccountActivationView  (views/account_activation.py)
    - PaymentVerificationView (views/verification.py)

Concerns per view:
    1. Context keys & values – the view puts the right variables into the
       template render call.
    2. Template data-* attributes – the rendered HTML carries every attribute
       that the client-side JS reads from #payment-container.
    3. Redirect guards – early-exit paths (unknown gateway, already paid,
       payment already completed) don't reach the template render.

Run with:
    pytest app/payments/tests/unit/views/test_account_activation_views.py -v
"""


import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from django.test import RequestFactory
from django.urls import reverse
from django.shortcuts import render, redirect
from core.url_names import PaymentURLS
from payments.domain.enums import PaymentStatus, PaymentType, PaymentPurpose, PaymentPhase, RegisteredPaymentProvider

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _mock_user(has_paid: bool = False) -> MagicMock:
    user = MagicMock()
    user.is_authenticated = True
    user.profile.has_paid_onetime_fee = has_paid
    return user


def _mock_entity(
    *,
    gateway_value: RegisteredPaymentProvider = RegisteredPaymentProvider.PAYSTACK,
    reference: str = "REF-TEST-001",
    status_value: PaymentStatus = PaymentStatus.PENDING,
) -> MagicMock:
    """
    Minimal stand-in for the payment domain entity returned by
    PaymentService.initiate_payment().
    """
    entity = MagicMock()
    entity.gateway = gateway_value
    entity.reference = reference
    entity.status = status_value
    return entity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rf() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def pending_entity():
    return _mock_entity()


@pytest.fixture
def paid_user():
    return _mock_user(has_paid=True)


@pytest.fixture
def unpaid_user():
    return _mock_user(has_paid=False)


# ---------------------------------------------------------------------------
# AccountActivationView – context tests
# ---------------------------------------------------------------------------


_PAYMENT_SERVICE_PATH = "payments.views.account_activation.PaymentService"
_MOCK_RENDER = "payments.views.account_activation.render"



class TestAccountActivationViewContext:
    """The GET handler must build the correct context before calling render()."""

    def _get_response(self, rf:RequestFactory, user, entity, gateway="paystack"):
        """Helper: patches PaymentService and returns the view response."""
        from payments.views.account_activation import AccountActivationView

        path = reverse(PaymentURLS.SUBSCRIPTION_CHECKOUT, kwargs={"gateway": gateway})
        request = rf.get(path)
        request.user = user
        
        view = AccountActivationView()
        view.request = request
        view.kwargs = {"gateway": gateway}
        view.user = user

        with patch(_PAYMENT_SERVICE_PATH) as MockService, \
             patch(_MOCK_RENDER) as mock_render:

            instance = MockService.return_value
            instance.initiate_payment.return_value = entity
            
            response = view.get(request, gateway=gateway)
            
            if mock_render.called:
                args, kwargs = mock_render.call_args
                
                # Extract context: usually the 3rd positional arg in render()
                # or provided as a keyword argument 'context'
                context_data = kwargs.get('context') or (args[2] if len(args) > 2 else {})
                response.context_data = context_data
            else:
                response.context_data = {}
            

        return response
    
    def test_context_contains_required_keys(self, rf, unpaid_user, pending_entity):
        response = self._get_response(rf, unpaid_user, pending_entity)
        assert "provider" in response.context_data, \
            "Context must include 'provider' – the template binds it to data-provider"
            
        assert "reference" in response.context_data, \
            "Context must include 'reference' – the template binds it to data-reference"
            
        assert "status" in response.context_data, \
            "Context must include 'status' – the template binds it to data-status"

    def test_invalid_gateway_returns_unregistered_template(self, rf, unpaid_user, pending_entity):
        response = self._get_response(rf, unpaid_user, pending_entity, gateway="unknown_gateway")
        assert response.context_data["provider"] == "unknown_gateway"

    def test_context_provider_equals_entity_gateway_value(self, rf, unpaid_user):
        entity = _mock_entity(gateway_value=RegisteredPaymentProvider.STRIPE)
        response = self._get_response(rf, unpaid_user, entity, gateway="stripe")
        assert response.context_data["provider"] == "stripe"

    def test_context_reference_equals_entity_reference(self, rf, unpaid_user):
        ref = "REF-UNIQUE-XYZ"
        entity = _mock_entity(reference=ref)
        response = self._get_response(rf, unpaid_user, entity)
        assert response.context_data["reference"] == ref

    def test_context_status_equals_entity_status(self, rf, unpaid_user):
        entity = _mock_entity(status_value=PaymentStatus.PENDING)
        response = self._get_response(rf, unpaid_user, entity)
        assert response.context_data["status"] == PaymentStatus.PENDING

    def test_provider_is_gateway_value_not_gateway_object(self, rf, unpaid_user):
        """Ensure entity.gateway.value is used, not the raw gateway enum/object."""
        entity = _mock_entity(gateway_value=RegisteredPaymentProvider.STRIPE)
        response = self._get_response(rf, unpaid_user, entity)
        assert isinstance(response.context_data["provider"], str)


# # ---------------------------------------------------------------------------
# # AccountActivationView – redirect guard tests
# # ---------------------------------------------------------------------------

# class TestAccountActivationViewRedirects:
#     """Early-exit paths must not reach the template render."""

#     def test_unknown_gateway_returns_unregistered_template(self, rf, unpaid_user):
#         from app.payments.views.account_activation import AccountActivationView

#         request = rf.get(reverse(PaymentURLS.ACCOUNT_ACTIVATION, kwargs={"gateway": "unknown"}))
#         request.user = unpaid_user

#         # GATEWAYS does not contain "unknown"
#         with patch(_GATEWAYS_PATH, {"paystack": MagicMock()}):
#             response = AccountActivationView.as_view()(request, gateway="unknown")

#         # Should render the unregistered-gateway template, not redirect
#         assert response.status_code == 200
#         assert "unknown" in response.context_data.get("provider", "")

#     def test_already_paid_user_is_redirected(self, rf, paid_user, pending_entity):
#         from app.payments.views.account_activation import AccountActivationView

#         request = rf.get("/payments/activate/paystack/")
#         request.user = paid_user  # has_paid_onetime_fee = True

#         with patch(_GATEWAYS_PATH, {"paystack": MagicMock()}), \
#              patch(_PAYMENT_SERVICE_PATH):
#             response = AccountActivationView.as_view()(request, gateway="paystack")

#         assert response.status_code == 302, \
#             "User who already paid must be redirected to payment summary"

#     @pytest.mark.parametrize("terminal_status", [PaymentStatus.SUCCESS, PaymentStatus.UNDERPAID])
#     def test_completed_payment_redirects_to_checkout_complete(
#         self, rf, unpaid_user, terminal_status
#     ):
#         from app.payments.views.account_activation import AccountActivationView
#         from app.payments.domain.enums import PaymentStatus  # adjust path

#         entity = _mock_entity(status_value=terminal_status)
#         # Map string to the actual enum so the `in {PaymentStatus.SUCCESS, ...}` check works
#         entity.status = getattr(PaymentStatus, terminal_status.upper(), terminal_status)

#         request = rf.get("/payments/activate/paystack/")
#         request.user = unpaid_user

#         with patch(_GATEWAYS_PATH, {"paystack": MagicMock()}), \
#              patch(_PAYMENT_SERVICE_PATH) as MockService:
#             MockService.return_value.initiate_payment.return_value = entity
#             response = AccountActivationView.as_view()(request, gateway="paystack")

#         assert response.status_code == 302, \
#             f"Status '{terminal_status}' must redirect to checkout-complete, not render template"


# # ---------------------------------------------------------------------------
# # AccountActivationView – template data-* attribute tests
# # ---------------------------------------------------------------------------

# @pytest.mark.django_db
# class TestAccountActivationTemplateAttributes:
#     """Rendered HTML must carry every data-* attribute the JS config reads."""

#     # From the JS block in the account-activation template:
#     #   container.dataset.status
#     #   container.dataset.reference
#     #   container.dataset.provider
#     #   container.dataset.endpoint
#     #   container.dataset.verificationUrl
#     #   container.dataset.summaryUrl
#     REQUIRED_DATA_ATTRS = [
#         "data-status",
#         "data-reference",
#         "data-provider",
#         "data-endpoint",
#         "data-verification-url",
#         "data-summary-url",
#     ]

#     REQUIRED_ELEMENT_IDS = [
#         "payment-container",
#         "network-log",
#         "payment-status-text",
#     ]

#     def _rendered_html(self, rf, unpaid_user, entity, gateway="paystack"):
#         from app.payments.views.account_activation import AccountActivationView

#         request = rf.get(f"/payments/activate/{gateway}/")
#         request.user = unpaid_user

#         with patch(_PAYMENT_SERVICE_PATH) as MockService, \
#              patch(_GATEWAYS_PATH, {gateway: MagicMock()}):
#             MockService.return_value.initiate_payment.return_value = entity
#             response = AccountActivationView.as_view()(request, gateway=gateway)

#         response.render()
#         return response.content.decode()

#     @pytest.mark.parametrize("attr", REQUIRED_DATA_ATTRS)
#     def test_payment_container_has_data_attribute(
#         self, attr, rf, unpaid_user, pending_entity
#     ):
#         html = self._rendered_html(rf, unpaid_user, pending_entity)
#         assert attr in html, \
#             f"Template is missing '{attr}' on #payment-container – JS will silently get undefined"

#     @pytest.mark.parametrize("element_id", REQUIRED_ELEMENT_IDS)
#     def test_required_element_ids_present(
#         self, element_id, rf, unpaid_user, pending_entity
#     ):
#         html = self._rendered_html(rf, unpaid_user, pending_entity)
#         assert f'id="{element_id}"' in html, \
#             f"Template is missing element with id='{element_id}'"

#     def test_csrf_token_present(self, rf, unpaid_user, pending_entity):
#         html = self._rendered_html(rf, unpaid_user, pending_entity)
#         assert 'name="csrfmiddlewaretoken"' in html, \
#             "CSRF token input must be present – JS reads it via querySelector"

#     def test_data_reference_value_matches_entity(self, rf, unpaid_user):
#         entity = _mock_entity(reference="REF-RENDER-CHECK")
#         html = self._rendered_html(rf, unpaid_user, entity)
#         assert "REF-RENDER-CHECK" in html

#     def test_data_provider_value_matches_entity(self, rf, unpaid_user):
#         entity = _mock_entity(gateway_value="paystack")
#         html = self._rendered_html(rf, unpaid_user, entity)
#         assert "paystack" in html


# ---------------------------------------------------------------------------
# PaymentVerificationView – context tests
# ---------------------------------------------------------------------------

# _VERIFICATION_VIEW_PATH = "app.payments.views.verification"
# _VERIFICATION_GATEWAYS_PATH = f"{_VERIFICATION_VIEW_PATH}.GATEWAYS"


# @pytest.mark.django_db
# class TestPaymentVerificationViewContext:
#     """GET must build the correct context: provider, reference, verificationUrl."""

#     def _get_response(self, rf, gateway="paystack", reference="REF-VER-001"):
#         from app.payments.views.verification import PaymentVerificationView

#         request = rf.get(
#             f"/payments/checkout/{gateway}/verify/",
#             data={"reference": reference},
#         )
#         request.user = _mock_user()

#         with patch(_VERIFICATION_GATEWAYS_PATH, {gateway: MagicMock()}):
#             response = PaymentVerificationView.as_view()(request, gateway=gateway)

#         return response

#     def test_context_has_provider_key(self, rf):
#         response = self._get_response(rf)
#         assert "provider" in response.context_data

#     def test_context_has_reference_key(self, rf):
#         response = self._get_response(rf)
#         assert "reference" in response.context_data

#     def test_context_has_verification_url_key(self, rf):
#         response = self._get_response(rf)
#         assert "verificationUrl" in response.context_data, \
#             "Context must include 'verificationUrl' – the template binds it to data-endpoint"

#     def test_context_provider_matches_url_kwarg(self, rf):
#         response = self._get_response(rf, gateway="stripe")
#         assert response.context_data["provider"] == "stripe"

#     def test_context_reference_matches_query_param(self, rf):
#         response = self._get_response(rf, reference="TXN-999")
#         assert response.context_data["reference"] == "TXN-999"

#     def test_context_reference_is_none_when_query_param_absent(self, rf):
#         """
#         When ?reference is not in the query string the view should not blow up;
#         reference will be None and the template must handle it gracefully.
#         """
#         from app.payments.views.verification import PaymentVerificationView

#         request = rf.get("/payments/checkout/paystack/verify/")  # no ?reference
#         request.user = _mock_user()

#         with patch(_VERIFICATION_GATEWAYS_PATH, {"paystack": MagicMock()}):
#             response = PaymentVerificationView.as_view()(request, gateway="paystack")

#         assert response.context_data["reference"] is None

#     def test_unknown_gateway_renders_unregistered_template(self, rf):
#         from app.payments.views.verification import PaymentVerificationView

#         request = rf.get("/payments/checkout/unknown/verify/")
#         request.user = _mock_user()

#         with patch(_VERIFICATION_GATEWAYS_PATH, {"paystack": MagicMock()}):
#             response = PaymentVerificationView.as_view()(request, gateway="unknown")

#         assert response.status_code == 200
#         assert "unknown" in response.context_data.get("provider", "")


# # ---------------------------------------------------------------------------
# # PaymentVerificationView – template data-* attribute tests
# # ---------------------------------------------------------------------------

# @pytest.mark.django_db
# class TestPaymentVerificationTemplateAttributes:
#     """
#     Rendered HTML must carry every attribute read by the verification JS:
#         container.dataset.reference
#         container.dataset.provider
#         container.dataset.endpoint
#     """

#     # Minimal set from the verification template's JS config block
#     REQUIRED_DATA_ATTRS = [
#         "data-reference",
#         "data-provider",
#         "data-endpoint",
#     ]

#     def _rendered_html(self, rf, gateway="paystack", reference="REF-VER-001"):
#         from app.payments.views.verification import PaymentVerificationView

#         request = rf.get(
#             f"/payments/checkout/{gateway}/verify/",
#             data={"reference": reference},
#         )
#         request.user = _mock_user()

#         with patch(_VERIFICATION_GATEWAYS_PATH, {gateway: MagicMock()}):
#             response = PaymentVerificationView.as_view()(request, gateway=gateway)

#         response.render()
#         return response.content.decode()

#     @pytest.mark.parametrize("attr", REQUIRED_DATA_ATTRS)
#     def test_payment_container_has_data_attribute(self, attr, rf):
#         html = self._rendered_html(rf)
#         assert attr in html, \
#             f"Verification template is missing '{attr}' on #payment-container"

#     def test_payment_container_id_present(self, rf):
#         html = self._rendered_html(rf)
#         assert 'id="payment-container"' in html

#     def test_data_reference_value_rendered_in_html(self, rf):
#         html = self._rendered_html(rf, reference="TXN-RENDER-42")
#         assert "TXN-RENDER-42" in html

#     def test_data_provider_value_rendered_in_html(self, rf):
#         html = self._rendered_html(rf, gateway="paystack")
#         assert "paystack" in html