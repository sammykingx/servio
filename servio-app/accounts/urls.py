from django.urls import path
from .views import auth

urlpatterns =[
    path("enlist/", auth.CustomSignup.as_view(), name="register"),
    path("access/", auth.CustomSignin.as_view(), name="login"),
    # magic link endpiont
]
