# Paystack webhook processing logic.

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from payments.domain.enums import RegisteredPaymentProvider, PaymentPhase
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import DomainException, PaymentPersistenceError
from payments.services.payment_service import PaymentService
import hashlib, hmac, json, logging


logger = logging.getLogger("payments")


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(View):
    def dispatch(self, request, *args, **kwargs):
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
        try:
            payload = json.loads(request.body)
            logger.info(f"Incoming Paystack Webhook: {payload}")
            event = payload.get('event')
            data = payload.get('data')
            reference = data.get("reference")
            if event == 'charge.success' and reference:
                self.handle_successful_charge(reference)
            return HttpResponse(status=200)
        
        except json.JSONDecodeError:
            return HttpResponse("Invalid data format", status=400)
        
        except DomainException as err:
            if err.code == PaymentFailure.SERVER_BUSY.code:
                HttpResponse(status=503)
            return HttpResponse(err, status=400)
        
        except Exception as err:
            logger.exception(err)
            return HttpResponse(status=500)
                    
    def handle_successful_charge(self, ref:str):
        """
        Processes a confirmed successful charge event by coordinating 
        with the domain service to verify and finalize the transaction.
        """
        service = PaymentService(
            gateway_name=RegisteredPaymentProvider.PAYSTACK, 
            phase=PaymentPhase.VERIFICATION
        )
        service.handle_webhook(ref)
