from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from template_map.collaboration import Collabs

# Create your views here.
class CollaborationListView(LoginRequiredMixin, TemplateView):
    template_name = Collabs.LIST_COLLABORATIONS