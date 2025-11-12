from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from typing import Any


class UserSignupForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    password2 = None
    
    user_model = get_user_model()
    
   
    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")
        if self.user_model.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "It seems you already have an account"
            )

        return email

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        return cleaned_data


    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
        )

