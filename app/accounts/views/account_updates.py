from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from accounts.models.socials import Platform
from accounts.models.address import AddressType
from collections import namedtuple
from template_map.accounts import Accounts


ValidationResult = namedtuple("ValidationResult", ["verified", "msg"])


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
    http_method_names = ["get", "post"]
    template_name = Accounts.ACCOUNT_EDIT_PROFILE
    
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        return render(request, self.template_name, {"profile": profile})
        # return JsonResponse({
        #     "profile": {
        #         "mobile_num": profile.mobile_num,
        #         "alt_mobile_num": profile.alt_mobile_num,
        #     }
        # })

    def post(self, request, *args, **kwargs) -> JsonResponse:
        profile = request.user.profile

        allowed_fields = ["mobile_num", "alt_mobile_num"]

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

