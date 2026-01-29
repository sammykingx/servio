from django.apps import apps
from django.db import IntegrityError,  transaction
from django.http import JsonResponse
from django.views.generic import TemplateView
from pydantic import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.onboarding.exception import OnboardingError
from accounts.onboarding.manager import UserOnboardingManager
from accounts.onboarding.schemas import OnboardingIntents
from accounts.onboarding.users.mixins import OnboardingStepMixin
from formatters.pydantic_formatter import format_pydantic_errors
from template_map.accounts import Accounts
import json


GigCategory = apps.get_model("collaboration", "GigCategory")
UserOnboardingIntent = apps.get_model("accounts", "UserOnboardingIntent")

class ObjectivesView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.OBJECTIVES
    view_step = 3
    
    def post(self, request, *args, **kwargs):
        manager = UserOnboardingManager(self.request.user)
        try:
            payload = json.loads(request.body)
            if payload.get("skip", False):
                return JsonResponse(
                    {"status": "success", "redirect_url": manager.advance_user()},
                    status=200
                )
            else:
                data = OnboardingIntents(**payload)
                intents = [intent.value for intent in data.intents]
                self.save_user_intents(intents)
        
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
                },
                status=400,
            )
        
        except OnboardingError as err:
            return JsonResponse(
                {
                    "error": err.title,
                    "message": err.message,
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
            {"status": "success", "redirect_url": manager.advance_user()},
            status=200
        )
        
    def save_user_intents(self, intents):
        with transaction.atomic():
            try:
                obj, created = UserOnboardingIntent.objects.get_or_create(
                    user=self.request.user,
                    defaults={"intents": intents},
                )

                if not created:
                    obj.intents = intents
                    obj.save()  # full_clean() runs here

                return obj

            except ValueError:
                raise OnboardingError(
                    title="Oopps!, Something went wrong",
                    message="We had trouble processing this request, we're working on it",
                )
                
            except IntegrityError as err:
                # log the error
                # Handles race condition where two requests hit at once
                raise OnboardingError(
                    title="Request already being processed",
                    message="We detected a recent submission. Please try again in a moment.",
                )
    

class CompleteOnboardingView(LoginRequiredMixin, OnboardingStepMixin, TemplateView):
    template_name = Accounts.Onboarding.COMPLETE
    view_step = 4