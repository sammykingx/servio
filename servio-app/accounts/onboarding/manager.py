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
    total_steps = 3
    success_url = reverse_lazy("".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.COMPLETE]))
    steps = {
        0: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.WELCOME]),
        1: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.PROFILE_SETUP]),
        2: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.EXPERTISE_AND_NICHE]),
        3: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.OBJECTIVES]),
    }
        
    def __init__(self, user):
        self.user = user
    
    @property    
    def user_step(self) -> int:
        return self.user.onboarding_step
        
    def is_complete(self) -> bool:
        return self.user.completed_onboarding
    
    def next_step_url(self) -> str:
        if self.user.completed_onboarding:
            return reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD)
        url = reverse_lazy(self.steps.get(self.user.onboarding_step, self.steps[0]))
        return url
    
    def should_advance(self) -> bool:
        if self.user.onboarding_step < self.total_steps:
            return True
        return False
    
    def advance_user(self) -> None:
        if self.should_advance():
            self.user.onboarding_step +=1
            self.user.save(update_fields=["onboarding_step"])
            
        else:
            if self.user.completed_onboarding:
                return reverse_lazy(AuthURLNames.ACCOUNT_DASHBOARD)
            
            self.user.onboarding_completed = True
            self.user.save(update_fields=["onboarding_completed"])
            return self.success_url
            
        
        return self.next_step_url()
    
    
class ProviderOnboardingManager:
    model = apps.get_model("business_accounts", "BusinessAccount")
    total_steps = 5
    
    def __init__(self, user):
        self.business = user
        
    def is_complete(self):
        return True