from django import forms
from django.apps import apps
# from django.forms import inlineformset_factory


# Gig = apps.get_model("collaboration","Gig")
# GigRole = apps.get_model("collaboration","GigRole")


# class GigCreateForm(forms.ModelForm):
#     class Meta:
#         model = Gig
#         fields = [
#             "title",
#             "visibility",
#             "description",
#             "start_date",
#             "end_date",
#             "total_budget",
#             "is_negotiable",
#         ]
        
# class GigRoleForm(forms.ModelForm):
#     class Meta:
#         model = GigRole
#         fields = [
#             "niche",
#             "role_title",
#             "budget",
#             "workload",
#             "is_negotiable",
#             "show_role_budget",
#         ]

# GigRoleFormSet = inlineformset_factory(
#     parent_model=Gig,
#     model=GigRole,
#     form=GigRoleForm,
#     extra=1,
#     can_delete=True,
# )