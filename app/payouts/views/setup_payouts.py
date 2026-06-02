from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View


class SavePayoutAccountView(LoginRequiredMixin, View):
    pass