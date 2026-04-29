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

import json, pytest
from core.url_names import PaymentURLS
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse
from payments.domain.enums import PaymentStatus, RegisteredPaymentProvider
from payments.views.account_activation import AccountActivationView
from template_map.payments import Payments
from unittest.mock import MagicMock, patch

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

    def _get_response(self, rf:RequestFactory, user:MagicMock, entity:MagicMock, gateway="paystack"):
        """Helper: patches PaymentService and returns the view response."""

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


class TestAccountActivationViewResponses:
    """Verifies that GET and POST handlers return the correct Templates, Redirects, or JSON."""
    
    def _setup_view(self, rf:RequestFactory, user:MagicMock, gateway, method="get", data=None):
        """Standardizes View initialization for both GET and POST."""
        
        path = reverse(PaymentURLS.SUBSCRIPTION_CHECKOUT, kwargs={"gateway": gateway})
        if method == "post":
            request = rf.post(path, data=json.dumps(data), content_type="application/json")
        else:
            request = rf.get(path)
            
        request.user = user
        view = AccountActivationView()
        view.request = request
        view.kwargs = {"gateway": gateway}
        view.user = user 
        return view, request

    def _get_response_with_mocks(self, view:AccountActivationView, request, gateway, entity=None):
        """Helper that patches dependencies and extracts template/context metadata."""
        
        with patch(_PAYMENT_SERVICE_PATH) as MockService, \
             patch(_MOCK_RENDER) as mock_render:
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_render.return_value = mock_response

            if entity:
                MockService.return_value.initiate_payment.return_value = entity
            
            response = view.get(request, gateway=gateway)
            
            if mock_render.called:
                args, kwargs = mock_render.call_args
                response.template_used = args[1]
                response.context_data = kwargs.get('context') or (args[2] if len(args) > 2 else {})
            else:
                response.template_used = None
                response.context_data = {}
                
            return response

    # --- GET TESTS ---
    def test_unknown_gateway_renders_unregistered_template(self, rf, unpaid_user):
        gateway = "unknown_gateway"
        view, request = self._setup_view(rf, unpaid_user, gateway)
        
        response = self._get_response_with_mocks(view, request, gateway)
        
        assert response.status_code == 200
        assert response.template_used == Payments.Checkouts.UNREGISTERED_GATEWAY
        assert response.context_data.get("provider") == gateway

    def test_valid_gateway_renders_checkout_template(self, rf, unpaid_user, pending_entity):
        gateway = RegisteredPaymentProvider.PAYSTACK.value
        view, request = self._setup_view(rf, unpaid_user, gateway)
        
        response = self._get_response_with_mocks(view, request, gateway, entity=pending_entity)
        
        assert response.status_code == 200
        assert response.template_used == Payments.Checkouts.PAYSTACK_CHECKOUT

    def test_already_paid_user_redirects_to_summary(self, rf, paid_user):
        gateway = RegisteredPaymentProvider.PAYSTACK.value
        view, request = self._setup_view(rf, paid_user, gateway)
        
        response = view.get(request, gateway=gateway)

        assert response.status_code == 302
        assert response.url == reverse(PaymentURLS.USER_PAYMENT_SUMMARY)
        

    # --- POST Tests: Logic & Exception Handling ---

    def _execute_post(self, rf, user, payload:dict, mock_resp=None, exception=None):
        """Helper for POST logic and Exception branches."""
        gateway = payload.get("provider", "paystack")
        view, request = self._setup_view(rf, user, gateway, method="post", data=payload)

        with patch(_PAYMENT_SERVICE_PATH) as MockService:
            service_instance = MockService.return_value
            if exception:
                service_instance.process_payment.side_effect = exception
            else:
                service_instance.process_payment.return_value = mock_resp or {}

            return view.post(request, gateway=gateway)

    def test_post_success_returns_json_manifest(self, rf, unpaid_user):
        payload = {"provider": "paystack", "reference": "REF-123"}
        mock_resp = {"message": "URL Ready", "data": {"checkout_url": "https://pay.me"}}
        
        response = self._execute_post(rf, unpaid_user, payload, mock_resp=mock_resp)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["data"]["checkout_url"] == "https://pay.me"

    def test_post_domain_exception_returns_400(self, rf, unpaid_user):
        from payments.domain.exceptions import DomainException
        payload = {"provider": "paystack", "reference": "REF-FAIL"}
        exc = DomainException(message="Insufficient funds", title="Payment Failed", code="PAYMENT_FAILED")
        exc.err_type = "warning"

        response = self._execute_post(rf, unpaid_user, payload, exception=exc)

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["title"] == "Payment Failed"
        assert data["ui_intent"] == "warning"


# ---------------------------------------------------------------------------
# AccountActivationView – template data-* attribute tests
# ---------------------------------------------------------------------------
class TestAccountActivationTemplateAttributes:
    """Ensures templates provide the necessary hooks for JavaScript integration."""

    # THE CONTRACT: Every checkout template must have these
    REQUIRED_IDS = [
        "payment-container",
        "network-log",
        "payment-status-text"
    ]
    
    REQUIRED_DATA_ATTRS = [
        "status",
        "reference",
        "provider",
        "endpoint",
        "verification-URL",
        "summary-URL",
    ]

    def _verify_template_contract(self, template_name, context):
        """Reusable engine to check any checkout template against the JS contract."""
        rf = RequestFactory()
        request = rf.get('/')
        request.user = MagicMock()
        html = render_to_string(template_name, context, request=request)
        
        for element_id in self.REQUIRED_IDS:
            assert f'id="{element_id}"' in html, f"Missing required ID: {element_id} in {template_name}"

        for attr in self.REQUIRED_DATA_ATTRS:
            assert f'data-{attr}=' in html, f"Missing data attribute: data-{attr} in {template_name}"

    @pytest.fixture
    def mock_context(self):
        """Standard context required for rendering."""
        return {
            "status": "pending",
            "reference": "REF-123",
            "provider": "paystack",
            "endpoint": "/api/pay/",
            "verification_url": "/verify/",
            "summary_url": "/summary/",
        }

    def test_paystack_template_adheres_to_js_contract(self, mock_context):
        """Verifies Paystack HTML has all JS hooks."""
        self._verify_template_contract(
            Payments.Checkouts.PAYSTACK_CHECKOUT, 
            mock_context
        )

    # def test_stripe_template_adheres_to_js_contract(self, mock_context):
    #     """Verifies Stripe HTML has all JS hooks (ensuring KISS & SOLID)."""
    #     self._verify_template_contract(
    #         Payments.Checkouts.STRIPE_CHECKOUT, 
    #         mock_context
    #     )
