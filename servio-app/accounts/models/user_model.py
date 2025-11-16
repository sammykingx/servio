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
    
    def verify_account(self) -> bool:
        if not self.is_verified:
            self.is_verified = True
            self.save(update_fields=["is_verified"])
        return True
        
    def deactivate_account(self) -> bool:
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active"])
            
        return True
        
    def __str__(self) -> str:
        return (
            f"{self.first_name} {self.last_name} "
            f"<{self.email}> "
            f"{'(verified)' if self.is_verified else '(not verified)'}"
        )
        
    def __repr__(self) -> str:
        return (
            f"AuthUser(first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"email={self.email!r}, "
            f"is_verified={self.is_verified!r}, "
            f"is_active={self.is_active!r})"
        )


    
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