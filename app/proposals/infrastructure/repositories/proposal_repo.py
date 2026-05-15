from core.model_registry import registry


class ProposalRepository:
    def  __init__(self):
        self.model = registry.Proposal