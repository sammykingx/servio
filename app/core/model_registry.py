from django.apps import apps

class ModelRegistry:
    """
    A dynamic registry that finds any model in the project automatically.
    """
    def __init__(self):
        # Optional: Map app labels if you have models with the same name in different apps
        # ModelName: app_name
        self._app_map = {
            'Proposal': 'collaboration',
            'ProposalRole': 'collaboration',
            'Gig': 'collaboration',
            'ProposalDeliverable': 'collaboration',
            
        }

    def __getattr__(self, name):
        # 1. Check if we have a specific app mapped for this model
        app_label = self._app_map.get(name, 'collaboration') # Default app
        
        try:
            return apps.get_model(app_label, name)
        except LookupError:
            # 2. If not found in default, search all apps for the model name
            for config in apps.get_app_configs():
                try:
                    return apps.get_model(config.label, name)
                except LookupError:
                    continue
            
            raise AttributeError(f"Model '{name}' not found in any registered app.")


models = ModelRegistry()
# usage models.ClaaName