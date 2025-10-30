from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


# Fields from django user models
    #   first_name, last_name, email, password,
    #   is_active, date_joined, last_login
    #   is_staff(can login into django admin), is_superuser(has all perms)
  
class AuthUser(AbstractUser):
    """
    Custom User model that uses email as the unique identifier instead of username.
    """
    username = None
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    @property
    def full_name(self):
        "Returns the person's full name."
        return f"{self.first_name} {self.last_name}"
    
    
    class Meta:
        db_table = "user_accounts"
        ordering = ["date_joined",]
        indexes = [
            models.Index(fields=["email"], name="email_idx",),
        ]
    
    
class CustomUserManager(BaseUserManager):
    # https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
    def create_user(self, *, email: str=None, password: str=None, **extra_fields) -> AbstractUser:
        if not (email and password):
            missing_field = "Email" if not email else "Password"
            raise ValueError(f"Missing {missing_field} Field.")
        
        user = self.model(
            email=self.normalize_email(email),
            date_joined=timezone.now(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user