from core.url_names import OnboardingURLS
from accounts.models.profile import UserRole

ONBOARDING_FLOWS = {
    UserRole.MEMBERS: [
            OnboardingURLS.Users.WELCOME,
            OnboardingURLS.Users.PROFILE_SETUP,
        ],
    UserRole.PROVIDERS: [],
}
