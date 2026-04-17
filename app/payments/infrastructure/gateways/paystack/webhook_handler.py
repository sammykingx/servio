# Paystack webhook processing logic.

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from payments.domain.enums import RegisteredPaymentProvider, PaymentPhase
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import DomainException, PolicyViolationError, PaymentPersistenceError
from payments.services.payment_service import PaymentService
import hashlib, hmac, json

@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(View):
    def dispatch(self, request, *args, **kwargs):
        # 1. Retrieve the signature from headers
        signature = request.headers.get('x-paystack-signature')
        
        if not signature:
            return HttpResponse("Missing signature", status=401)

        secret_key = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_hmac = hmac.new(
            secret_key,
            msg=request.body,
            digestmod=hashlib.sha512
        ).hexdigest()

        if not hmac.compare_digest(computed_hmac, signature):
            return HttpResponse("Invalid signature", status=401)

        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        event = payload.get('event')
        data = payload.get('data')
        reference = data.get("reference")
        if event == 'charge.success':
            try:
                service = PaymentService(gateway_name=RegisteredPaymentProvider.PAYSTACK, phase=PaymentPhase.VERIFICATION)
                service.verify(reference)
                return HttpResponse(status=200)
            except PaymentPersistenceError as err:
                if err.code == PaymentFailure.SERVER_BUSY:
                    HttpResponse(status=503)
