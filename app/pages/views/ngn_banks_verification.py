from django.core.cache import caches
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from payments.infrastructure.gateways.adapters.paystack import PaystackAdapter


class RenderNGNBankListView(View):
    CACHE_KEY = "paystack_ngn_banks"
    CACHE_TTL = 60 * 60 * 24 * 180 # 180 ddays
    
    def get(self, request: HttpRequest, *args, **kwargs):
        file_cache = caches["file_cache"]
        cached_banks = file_cache.get(self.CACHE_KEY)
        if cached_banks is not None:
            return JsonResponse({"banks": cached_banks})
        
        adapter = PaystackAdapter(request)
        ngn_banks = adapter.get_ngn_banks()
        banks = [
            bank
            for bank in ngn_banks
            if bank.get("supports_transfer", False)
        ]
        file_cache.set(self.CACHE_KEY, banks, self.CACHE_TTL)
        return JsonResponse({"banks": banks})
    

class VerifyBankAccountView(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        account_number = request.GET.get("account_number")
        bank_code = request.GET.get("bank_code")
        if not account_number or not bank_code:
            return JsonResponse({"error": "Account number and bank code are required."}, status=400)
        
        adapter = PaystackAdapter(request)
        verification_result = adapter.resolve_account_number(account_number, bank_code)
        if verification_result.get("status") is True:
            return JsonResponse(verification_result.get("data"))
        else:
            return JsonResponse({"error": "Bank account verification failed."}, status=400)