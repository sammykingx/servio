from allauth.account.forms import SignupForm
from django import forms


class UserSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    
    def save(self, request):
        print("form save method")

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        # user = super().save(request)
        print("super method in form class")

        # Add your own processing here.

        # You must return the original result.
        