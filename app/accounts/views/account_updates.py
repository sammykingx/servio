from django.views import View
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from accounts.models.socials import Platform
from accounts.models.address import AddressType
from accounts.exceptions import ProfileUpdateError
from accounts.validators import UserProfileUpdatePayload, UserAddressUpdatePayload
from collections import namedtuple
from template_map.accounts import Accounts
from pydantic import ValidationError
import json, logging

logger = logging.getLogger("django")


ValidationResult = namedtuple("ValidationResult", ["verified", "msg"])
MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

class UpdateSocialLinksView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs) -> HttpResponse:
        user = request.user
        platform_map = dict(Platform.choices)

        for platform_name in platform_map.keys():
            url = request.POST.get(platform_name, None)
            if url:
                social_link, created = user.social_links.update_or_create(
                    platform=platform_name,
                    defaults={"url": url},
                )

        return JsonResponse(
            {
                "status": "success",
                "message": "Social links updated successfully.",
            }
        )


class UpdateProfilePictureView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        uploaded_file = request.FILES.get("profile_image")

        if not uploaded_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)
        
        if uploaded_file.size > MAX_PROFILE_IMAGE_SIZE:
            return JsonResponse(
                {"error": "File size exceeds limits"},
                status=400,
            )

        if uploaded_file.content_type not in ALLOWED_IMAGE_TYPES:
            return JsonResponse(
                {"error": "Unsupported media type"},
                status=400,
            )

        uploaded_file.name = self.build_filename(profile, uploaded_file.name)
        self.save_profile_img(profile, uploaded_file)
        

        return JsonResponse(
            {
                "message": "Profile picture updated successfully",
                "avatar_url": profile.avatar_url.url,
            }
        )

    def save_profile_img(self, profile, uploaded_file) -> None:
        if profile.avatar_url:
            profile.avatar_url.delete(save=False)

        profile.avatar_url = uploaded_file
        profile.save()

        return None
    
    def build_filename(self, profile, original_name):
        import os, nanoid
        seed = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ext = os.path.splitext(original_name)[1].lower()
        
        return f"prf-img_{nanoid.generate(seed, 13)}{ext}"


class UpdateAddressView(LoginRequiredMixin, View):
    http_method_names = ["post"]
    UPDATE_FIELDS = ["street", "street_line_2", "city", "province", "postal_code", "country"]


    def post(self, request, *args, **kwargs):
        user = request.user
        created, updated = False, False
        data = {
            key: value.lower()
            for key, value in request.POST.dict().items()
            if key != "csrfmiddlewaretoken"
        }

        res = self.verify_data(data)
        if not res.verified:
            return JsonResponse({"status": "error", "message": res.msg})
        
        address_qs = user.addresses.filter(label=data.get("label"))
        if address_qs.exists():
            address = address_qs.first()
            updated = self.update_fields(address, data)
            
        else:
            address = user.addresses.model(user=user, **data)
            created = True

        if updated or created:
            address.save()
        
        message = (
            "Your address has been successfully added." if created else
            "Your address has been successfully updated." if updated else
            "No changes were made to your address."
        )

        return JsonResponse({
            "status": "success",
            "message": message,
            "address": {
                "street": address.street,
                "street_line_2": address.street_line_2,
                "city": address.city,
                "province": address.province,
                "postal_code": address.postal_code.upper(),
                "country": address.country,
                "label": address.label,
            }
        })

    def verify_data(self, data:dict) -> ValidationResult:
        label = data.get("label", AddressType.HOME).lower()

        if label not in AddressType.values:
            return ValidationResult(
                verified=False,
                msg=f"Invalid address type '{label}'. Please choose a valid type."
            )

        allowed_keys = set(self.UPDATE_FIELDS + ["label"])
        if not all(key in allowed_keys for key in data.keys()):
            invalid_keys = [key for key in data.keys() if key not in allowed_keys]
            return ValidationResult(
                verified=False,
                msg=f"Invalid field(s) provided: {', '.join(invalid_keys)}."
            )

        return ValidationResult(verified=True, msg="Data verified successfully.")
        
    def update_fields(self, address, data) -> bool:
        updated = False
        for field in self.UPDATE_FIELDS:
            new_value = data.get(field, "").strip()
            if new_value and getattr(address, field, None) != new_value:
                setattr(address, field, new_value)
                updated = True
        return updated


class UpdatePersonalInfoView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs) -> JsonResponse:
        profile = request.user.profile
        allowed_fields = ["bio", "mobile_num", "alt_mobile_num", "headline"]
        updated_fields = {}

        for field in allowed_fields:
            value = request.POST.get(field, "").strip()
            setattr(profile, field, value)
            updated_fields[field] = value or ""

        profile.save()
        
        return JsonResponse(
                {
                    "status": "success",
                    "message": "Personal information updated successfully.",
                    "profile": updated_fields,
                }
            )


class UpdateUserProfileView(LoginRequiredMixin, View):
    """
        View for displaying and updating the authenticated user's profile.

        Handles rendering the profile edit page (GET) and processing profile,
        address, and social link updates (POST). All updates are validated,
        performed atomically, and return JSON responses indicating success
        or failure.
    """
    http_method_names = ["get", "post"]
    template_name = Accounts.ACCOUNT_EDIT_PROFILE
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs) -> JsonResponse:
        """
            Process profile update requests.

            Expects a JSON payload containing profile details, address information,
            and social links. Validates input data, performs updates atomically,
            and returns a JSON response indicating success or an appropriate error.
        """
        try:
            data = json.loads(request.body)
            profile_payload = UserProfileUpdatePayload(**data.get("profile", {}))
            address_payload = UserAddressUpdatePayload(**data.get("address", {}))
            social_links_payload = data.get("social_links", {})
            self.process_profile_update(profile_payload, address_payload, social_links_payload)
            
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        
        except ValidationError as err:
            for e in err.errors():
                message = f"{e['msg']}"
            return JsonResponse({"status": "error", "message": message}, status=400)
        
        except ProfileUpdateError as err:
            return JsonResponse({"status": "error", "message": err}, status=400)
        
        except Exception:
            return JsonResponse(
                {
                    "status": "error", 
                    "message": "Sorry about that! Our service is having a moment. Please try again in a bit."
                },
                status=400
            )
        
        return JsonResponse({
            "status": "success",
            "message": "Nice work! Your profile changes have been saved 😄.",
        })
        
    def update_personal_info(self, profile_obj, personal_info:UserProfileUpdatePayload):
        """
            Update the user's personal profile information.

            Maps validated payload fields to profile model fields and persists
            the changes efficiently using partial updates.
        """
        
        PROFILE_FIELD_MAP = {
            "bio": "bio",
            "headline": "headline",
            "mobile_number": "mobile_num",
            "alternate_number": "alt_mobile_num",
        }
        
        for payload_field, model_field in PROFILE_FIELD_MAP.items():
            if hasattr(personal_info, payload_field):
                value = getattr(personal_info, payload_field)
                setattr(profile_obj, model_field, value)

        profile_obj.save(update_fields=PROFILE_FIELD_MAP.values())
        
    def update_social_links(self, social_links:dict):
        """
            Create or update the user's social media links.

            Validates supported platforms and ensures each social link is
            updated or created for the authenticated user.
        """
        user = self.request.user
        platform_map = dict(Platform.choices)
        for platform_name, url in social_links.items():
            if platform_name in platform_map:
                user.social_links.update_or_create(
                    platform=platform_name,
                    defaults={"url": url},
                )
    
    def update_address(self, home_address_obj, address_payload:UserAddressUpdatePayload):
        """
            Update the user's home address information.

            Applies validated address payload fields to the address model
            and saves the changes using partial updates.
        """
        address_info = address_payload.model_dump()
        for field, value in address_info.items():
            setattr(home_address_obj, field, value)
        home_address_obj.save(update_fields=address_info.keys())
            
    def process_profile_update(self, profile_data:UserProfileUpdatePayload, address_data:UserAddressUpdatePayload, social_links:dict):
        """
            Orchestrate the complete user profile update process.

            It receives validated data, locks related records, and updates profile,
            address, and social links within a single atomic transaction.
            Raises domain-specific errors for validation, integrity, or
            unexpected failures.
        """
        if not profile_data:
            raise ProfileUpdateError("Profile data is required")

        if not address_data:
            raise ProfileUpdateError("Address data is required")

        if not social_links:
            raise ProfileUpdateError("Social links are required")
        
        user = self.request.user
        
        with transaction.atomic():
            try:
                profile_obj = (
                    user.profile.__class__
                    .objects.select_for_update()
                    .get(user=user)
                )
                self.update_personal_info(profile_obj, profile_data)
                
                home_address_qs = user.addresses.filter(label=AddressType.HOME)
                if home_address_qs.exists():
                    home_address = home_address_qs.select_for_update().first()
                    self.update_address(home_address, address_data)
                else:
                    home_address = user.addresses.model(user=user, **address_data.model_dump())
                    home_address.save()

                self.update_social_links(social_links)
                
            except IntegrityError:
                logger.exception("Integrity error during profile update for user=%s", user)
                raise ProfileUpdateError(
                    "We couldn't save some of your information because of a conflict. "
                    "Please check for duplicates or try again."
                )
                
            except Exception as err:
                logger.exception(
                    "Profile update failed for user = > %s",
                    self.request.user,
                )
                raise