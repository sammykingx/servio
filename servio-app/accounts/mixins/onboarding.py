# not used yet
from django.shortcuts import redirect
from django.urls import reverse
from accounts.models.profile import UserRole
from typing import Union


class OnboardingRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

