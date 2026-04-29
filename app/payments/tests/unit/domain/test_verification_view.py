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