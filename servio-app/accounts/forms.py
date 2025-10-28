from allauth.account.forms import SignupForm
from django import forms


class UserSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    
    def save(self, request):
        user = super().save(request)
        # Set additional user fields and then call user.save()
        return user
