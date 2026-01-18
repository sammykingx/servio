class OnboardingError(Exception):
    """
    Exception for onboarding flow errors.

    - title/message: safe for UI
    - internal_reason: logged only (never shown to users)
    """

    def __init__(
        self,
        title: str,
        message: str,
        internal_reason: str | None = None,
    ):
        self.title = title
        self.message = message
        self.internal_reason = internal_reason
        super().__init__(message)
