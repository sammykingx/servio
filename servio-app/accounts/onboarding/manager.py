from django.contrib.auth import get_user_model
from django.apps import apps
from django.urls import reverse_lazy
from accounts.models.profile import UserRole
from core.url_names import AuthURLNames, OnboardingURLS


def resolve_onboarding_manager(user):
    if user.groups.filter(name=UserRole.MEMBERS).exists():
        return UserOnboardingManager(user)

    if user.groups.filter(name=UserRole.PROVIDERS).exists():
        return ProviderOnboardingManager(user)

    return None


class UserOnboardingManager:
    model = get_user_model()
    total_steps = 4
    success_url = reverse_lazy("".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.COMPLETE]))
    steps = {
        0: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.WELCOME]),
        1: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.PROFILE_SETUP]),
        2: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.EXPERTISE_AND_NICHE]),
        3: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.OBJECTIVES]),
        4: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.COMPLETE]),
    }
        
    def __init__(self, user):
        self.user = user
    
    @property    
    def user_step(self) -> int:
        return self.user.onboarding_step
    
    @property   
    def has_completed(self) -> bool:
        if self.user.onboarding_step < self.total_steps:
            return True
        return False
        
    def is_complete(self) -> bool:
        return self.user.completed_onboarding
    
    def next_step_url(self) -> str:
        return reverse_lazy(self.steps.get(self.user.onboarding_step, self.steps[0]))
    
    def increase_step(self):
        self.user.onboarding_step +=1
        self.user.save(update_fields=["onboarding_step"])
        
    def mark_complete(self) -> None:
        self.user.onboarding_completed = True
        self.user.save(update_fields=["onboarding_completed"])
    
    def advance_user(self) -> None:
        self.increase_step()
        if self.has_completed:
           self.mark_complete()
           return self.success_url
        return self.next_step_url()
    
    
class ProviderOnboardingManager:
    model = apps.get_model("business_accounts", "BusinessAccount")
    total_steps = 5
    
    def __init__(self, user):
        self.business = user
        
    def is_complete(self):
        return True