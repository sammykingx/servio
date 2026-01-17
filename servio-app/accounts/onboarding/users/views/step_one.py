from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from pydantic import ValidationError
from template_map.accounts import Accounts
from accounts.models.address import AddressType
from accounts.onboarding.users.mixins import OnboardingStepMixin
from accounts.onboarding.manager import UserOnboardingManager
from accounts.onboarding.schemas import AddressPayload, ProfilePayLoad, NumberPayload
from formatters.pydantic_formatter import format_pydantic_errors
import json


class StartOnboardingView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.START_FLOW
    view_step = 0
    
    def post(self, request, *args, **kwargs):
        manager = UserOnboardingManager(self.request.user)
        return JsonResponse(
            {"redirect_url": manager.advance_user()}, 
            status=200
        )

class PersonalInfoView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.PERSONAL_INFO
    view_step = 1
    
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            data = ProfilePayLoad(**payload)
            self.update_profile_info(data.profile, data.address)
            manager = UserOnboardingManager(self.request.user)
        
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload",
                    "message": "Request body should be a valid JSON data, check and try again.",
                },
                status=400,
            )
        
        except ValidationError as e:
            return JsonResponse(
                {
                    "error": "Validation error",
                    "message": "Some required information is missing or invalid.",
                    "fields": format_pydantic_errors(e),
                },
                status=400,
            )
        
        except IntegrityError as e:
            return JsonResponse(
                {
                    "error": "Operation error",
                    "message": "Action already in progress, please try again in a moment.",
                },
                status=400,
            )
            
        except Exception:
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {
                    "error": "Something went wrong",
                    "message": "We couldn’t complete your request. Please try again shortly.",
                },
                status=400,
            )

        return JsonResponse(
            {"redirect_url": manager.advance_user()}, 
            status=200
        )
        
    def update_profile_info(self, profile_data:NumberPayload, address_data:AddressPayload):
        from django.apps import apps
        
        AddressModel = apps.get_model("accounts", "Address")
        
        with transaction.atomic():
            user = self.request.user
            
            user.profile.mobile_num = profile_data.phoneCountryCode + profile_data.phoneNumber
            user.profile.alt_mobile_num = profile_data.altNumber if profile_data.altNumber else None
            
            user.profile.save(update_fields=["mobile_num", "alt_mobile_num"])
             
            address, created = AddressModel.objects.select_for_update().get_or_create(
                user=user,
                label=AddressType.HOME,
                defaults={
                    "street": address_data.street,
                    "street_line_2": address_data.street_line_two,
                    "city": address_data.city,
                    "province": address_data.state,
                    "country": address_data.country,
                    "postal_code": address_data.postal_code,
                    "is_default": True,
                },
            )

            if not created:
                address.street = address_data.street
                address.street_line_2 = address_data.street_line_two
                address.city = address_data.city
                address.province = address_data.state
                address.country = address_data.country
                address.postal_code = address_data.postal_code
                address.is_default = True

                address.save()

            # Ensure it's the ONLY default
            (
                AddressModel.objects
                .filter(user=user)
                .exclude(pk=address.pk)
                .update(is_default=False)
            )