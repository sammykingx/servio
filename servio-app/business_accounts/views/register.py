from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.repositories.social_links import SocialLinkRepository
from business_accounts.repositories.business_accounts import BusinessAccountsRepository
from template_map.accounts import Accounts
import json


class BusinessInfoView(LoginRequiredMixin, TemplateView):
    """
    View to display the user's business settings page.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from constants import biz_categories
        context["industry_obj"] = biz_categories.get_industry_obj()
        
        return context

    template_name = Accounts.Business.BUSINESS_INFO
    
    
class RegisterBusinessAccount(LoginRequiredMixin, View):
    http_method_names = ["post"]
    
    def post(self, request, *args, **kwargs):
        try:
            business_data, address_data, socials_data = self.parse_and_validate_payload(request)

            self.process_business_account(
                request.user,
                business_data,
                address_data,
                socials_data
            )

        except ValidationError as e:
            return JsonResponse({"error": e.message}, status=400)
        except Exception:
            return JsonResponse(
                {"error": "Something went wrong. Please contact support team for assistance."},
                status=500
            )

        return JsonResponse(
            {"status": "success", "message": "Business account registered successfully."},
            status=201
        )
    
    def parse_and_validate_payload(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON payload.")

        if not self.validate_payload(payload):
            raise ValidationError("Bad/Incomplete request data")

        return self.serialize_payload(payload)

    def process_business_account(self, user, business_data, address_data, socials_data):
        address_obj = self.save_business_address(address_data)
        business_acct = BusinessAccountsRepository.create_business_account(
            user, address_obj, business_data
        )
        print(type(business_acct))
        if socials_data:
            SocialLinkRepository.create_or_update_socials(
                socials_data,
                business=business_acct.instance
            )

        return business_acct
    
    def validate_payload(self, payload):
        required_keys = {
            'name', 'tagline', 'email', 'phone', 'industry',
            'niche', 'bio', 'socials', 'address'
        }
        required_socials_keys = {'facebook', 'instagram', 'twitter', 'linkedin'}
        required_address_keys = {'street', 'streetTwo', 'city', 'state', 'postalCode', 'country'}
        
        if not required_keys.issubset(payload.keys()):
            return False
        if not required_socials_keys.issubset(payload.get('socials', {}).keys()):
            return False
        if not required_address_keys.issubset(payload.get('address', {}).keys()):
            return False
        
        return True

    def serialize_payload(self, payload):
        business = {
            key: value.lower()
            for key, value in payload.items() if key not in ["socials", "address"]
        }
        address = {
            key: value.lower()
            for key, value in payload["address"].items() if value
        }
        socials = {
            key: value.lower()
            for key, value in payload["socials"].items() if value
        }
        
        return business, address, socials
    
    def save_business_address(self, data):
        from accounts.models.address import AddressType
        
        user = self.request.user
        existing_address = user.addresses.filter(
            label=AddressType.WORK,
            is_business_address=True
        ).first()

        if existing_address:
            return existing_address
        try:
            address = user.addresses.create(
                street=data.get("street"),
                street_line_2=data.get("streetTwo"),
                city=data.get("city"),
                province=data.get("state"),
                country=data.get("country"),
                postal_code=data.get("postalCode"),
                is_business_address=True,
                label=AddressType.WORK
            )
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()

        return address
