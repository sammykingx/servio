from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.socials import Platform


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

        self.save_profile_img(profile, uploaded_file)

        print(uploaded_file.name)

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


class UpdateAddressView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs) -> HttpResponse:
        user = request.user
        return HttpResponse("Social links updated successfully.")


class UpdatePersonalInfoView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs) -> JsonResponse:
        profile = request.user.profile
        payload = {
            "mobile_num": request.POST.get("mobile_num"),
            "alt_mobile_num": request.POST.get("alt_mobile_num"),
        }

        for field, value in payload.items():
            if value:
                setattr(profile, field, value)
        profile.save()

        return JsonResponse(
            {
                "status": "success",
                "message": "Personal information updated successfully.",
            }
        )
