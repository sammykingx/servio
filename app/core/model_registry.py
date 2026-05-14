from django.apps import apps
from django.db.models import Model


class ModelRegistry:
    """
        Centralised registry for resolving Django models via `apps.get_model()`.

        All models are declared explicitly in `_registry` as ("app_label", "ModelName")
        pairs. Resolution is lazy — models are looked up at access time, not import
        time, avoiding AppRegistryNotReady errors. Django's internal app registry
        handles caching, so there is no performance cost to resolving fresh each time.


        USAGE
        -----
        Anywhere in the project (views, repositories, signals, tasks, serializers):

            from core.model_registry import registry

            # Resolve a model
            Proposal = registry.Proposal
            
            # or
            registry.Contract.objects.filter(status='active')

        MAINTENANCE
        -----------
        To add a new model, add one line to `_registry`:

            "ModelName": ("app_label", "ModelName")

        To rename an app, update the app_label in every entry for that app — still
        all in this one file, nowhere else.

        ERRORS
        ------
        - Accessing an unregistered name raises AttributeError with a clear message
        directing you to add the entry to `_registry`.
        - A mismatched app_label or model_name raises LookupError with the exact
        entry that needs fixing.
    """

    _registry: dict[str, tuple[str, str]] = {
        # "ModelName": ("app_label", "ModelName")

        # ACCOUNTS APP
        "Address": ("accounts", "Address"),
        "Profile": ("accounts", "Profile"),
        "SocialLink": ("accounts", "SocialLink"),
        "Tokentype": ("accounts", "Tokentype"),
        "UserOnboardingIntent": ("accounts", "UserOnboardingIntent"),

        # GIG/PROJECTS/SERVICE REQUEST APP
        "Gig": ("collaboration", "Gig"),
        "GigRole": ("collaboration", "GigRole"),
        "GigCategory": ("collaboration", "GigCategory"),
        
        # CONTRACTS APP
        "Contract": ("contracts", "Contract"),
        
        # NOTIFICATIONS APP
        "NotificationChannels": ("notifications", "NotificationChannels"),
        "WebPushDeviceToken": ("notifications", "WebPushDeviceToken"),

        # PAYMENTS APP
        "Payment": ("payments", "Payment"),

        # PROPOSAL APP
        "Proposal": ("proposals", "Proposal"),
        "ProposalRole": ("proposals", "ProposalRole"),
        "ProposalDeliverable": ("proposals", "ProposalDeliverable"),
    }

    def __getattr__(self, name: str) -> Model:
        if name not in self._registry:
            raise AttributeError(
                f"Model '{name}' is not registered. "
                f"Add it to ModelRegistry._registry before using it."
            )

        app_label, model_name = self._registry[name]

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError as e:
            raise LookupError(
                f"Model '{model_name}' not found in app '{app_label}'. "
                f"Check the app_label in ModelRegistry._registry."
            ) from e

        return model

registry = ModelRegistry()
