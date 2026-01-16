from django.contrib.auth import get_user_model
from django.apps import apps
from django.urls import reverse_lazy
from accounts.models.profile import UserRole
from core.url_names import OnboardingURLS


def resolve_onboarding_manager(user):
    if user.groups.filter(name=UserRole.MEMBERS).exists():
        return UserOnboardingManager(user)

    if user.groups.filter(name=UserRole.PROVIDERS).exists():
        return ProviderOnboardingManager(user)

    return None


class UserOnboardingManager:
    model = get_user_model()
    total_steps = 4
    steps = {
        0: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.WELCOME]),
        1: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.PROFILE_SETUP]),
        2: "".join([OnboardingURLS.Users.APP_NAME, ":", OnboardingURLS.Users.EXPERTISE_AND_NICHE]),
        3: "".join([OnboardingURLS.Users.APP_NAME, ":",OnboardingURLS.Users.OBJECTIVES]),
        4: "".join([OnboardingURLS.Users.APP_NAME, ":",OnboardingURLS.Users.COMPLETE]),
    }
        
    def __init__(self, user):
        self.user = user
        
    def is_complete(self) -> bool:
        if not self.user.onboarding_completed:
            return False
            
        # self.user.completed_onboarding = True
        # self.user.save(update_fields=["onboarding_completed"])
        
        return True
    
    def next_step(self) -> str:
        return reverse_lazy(self.steps.get(self.user.onboarding_step, 0))
    
    
class ProviderOnboardingManager:
    model = apps.get_model("business_accounts", "BusinessAccount")
    total_steps = 5
    
    def __init__(self, user):
        self.business = user
        
    def is_complete(self):
        return True