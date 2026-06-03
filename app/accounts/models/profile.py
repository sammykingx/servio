from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from constants import SERVICE_FEE, SUBSRIBERS_SERVICE_FEE, DECIMAL_PLACE, USD_TO_NGN_RATE


class UserRole(models.TextChoices):
    MEMBERS = "member", "Members"
    PROVIDERS = "provider", "Providers"
    ADMIN = "admin", "Admin" # not used
    STAFF = "staff", "Staff" # not used


class UserProfile(models.Model):
    """
    Extended profile for AuthUser (One-to-One relationship).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        to_field="email",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    
    mobile_num = models.CharField(
        max_length=18, unique=True, blank=True, null=True
    )
    
    alt_mobile_num = models.CharField(
        max_length=20, blank=True, null=True
    )
    
    industry = models.ForeignKey(
        "collaboration.GigCategory",
        on_delete=models.SET_NULL,
        related_name="user_profiles",
        null=True,
        blank=True,
        limit_choices_to={"parent__isnull": True},
        help_text="Primary industry (top-level category)",
    )

    niches = models.ManyToManyField(
        "collaboration.GigCategory",
        related_name="profiles_niches",
        blank=True,
        limit_choices_to={"parent__isnull": False},
        help_text="Selected niches (subcategories under industry)",
    )

    bio = models.TextField(
        max_length=600,
        blank=True,
        help_text="Professional bio shown on public profile",
    )
    
    headline = models.CharField(
        max_length=50,
        blank=True,
        help_text="Short headline shown on public profile",
    )
    
    avatar_url = models.ImageField(
        upload_to="avatars/", null=True, blank=True
    )
    
    date_of_birth = models.DateField(blank=True, null=True)
    is_business_owner = models.BooleanField(default=False)
    has_paid_onetime_fee = models.BooleanField(default=False)
    
    role = models.CharField(
        choices=UserRole.choices,
        default=UserRole.MEMBERS,
        max_length=30,
    )


    class Meta:
        db_table = "user_profiles"
        
    
    @property
    def social_links(self):
        return {
            link.platform: link.url
            for link in self.user.social_links.all()
        }
        
    @property
    def home_address(self):
        return self.user.addresses.filter(label="home").first()
    
    @property
    def billing_info(self):
        return self.user.addresses.filter(label="billing").first()
    
    @property
    def get_user_niches(self) -> list:
        return self.niches.values_list("id", flat=True)
    
    @property
    def service_fee_percentage(self) -> Decimal:
        """
        Returns the raw service fee percentage rate based on user payment status.
        """
        if self.has_paid_onetime_fee:
            return Decimal(str(SUBSRIBERS_SERVICE_FEE))
        return Decimal(str(SERVICE_FEE))
    
    @property
    def service_fee_percentage_display(self) -> str:
        """
        Returns the service fee percentage rate formatted for display (e.g., '4%' or '17.5%').
        """
        if self.has_paid_onetime_fee:
            rate = float(SUBSRIBERS_SERVICE_FEE) * 100
        else:
            rate = float(SERVICE_FEE) * 100

        return f"{rate:g}%"
    
    def all_user_niches(self):
        return self.niches.all()
    
    def paid_one_time_fee(self):
        if not self.has_paid_onetime_fee:
            self.has_paid_onetime_fee = True
            self.save(update_fields=["has_paid_onetime_fee"])

    def get_niche_roles_list(self) -> list:
        """
        Returns a list of dictionaries detailing the user's selected niches
        and their parent industry categories.

        Note:
            The 'can_apply' attribute is intentionally included for each role 
            to streamline dynamic frontend rendering and simplify backend 
            validation during proposal submission.
        """
        roles = []
        user_niches = self.niches.select_related('parent').all()
        
        for niche in user_niches:
            roles.append({
                "niche_id": niche.parent.id if niche.parent else None,
                "niche_name": niche.parent.name if niche.parent else None,
                "role_id": niche.id,
                "role_name": niche.name,
                "can_apply": True
            })
            
        return roles
    
    def calculate_service_fee(self, amount: Decimal) -> Decimal:
        """
        Calculates the service fee amount for a given base amount 
        using the user's specific fee percentage tier.
        """
        
        return (
            Decimal(str(amount)) * self.service_fee_percentage
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
        
    def service_fee_to_ngn(self, amount: Decimal) -> Decimal:
        """
        Converts the calculated service fee to NGN using the current exchange rate.
        """
        fee = self.calculate_service_fee(amount)
        return (
            fee * Decimal(str(USD_TO_NGN_RATE))
        ).quantize(Decimal(str(DECIMAL_PLACE)), rounding=ROUND_HALF_UP)
    