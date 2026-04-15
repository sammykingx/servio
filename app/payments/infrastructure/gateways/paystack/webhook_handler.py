# Paystack webhook processing logic.

from django.http import HttpResponse
from payments.domain.enums import RegisteredPaymentProvider, PaymentPhase
from payments.domain.errors import PaymentFailure
from payments.domain.exceptions import DomainException, PolicyViolationError, PaymentPersistenceError
from payments.services.payment_service import PaymentService
from
import json

def payment_webhook(request):
    payload = json.loads(request.body)
    ref = payload['data']['reference']
    
    service = PaymentService(gateway_name=RegisteredPaymentProvider.PAYSTACK, phase=PaymentPhase.VERIFICATION)
    try:
        service.verify(ref)
        return HttpResponse(status=200)
    except PaymentPersistenceError as err:
      if err.code == PaymentFailure.SERVER_BUSY:
           HttpResponse(status=503)
    
