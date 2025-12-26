from django.core.exceptions import ValidationError
from django.apps import apps
from dataclasses import dataclass
from typing import TypeVar

BusinessAccount = TypeVar("BusinessAccount")


@dataclass(frozen=True)
class CreateResult:
    instance: BusinessAccount
    created: bool

class BusinessAccountsRepository:
    BusinessAccounts = apps.get_model("business_accounts", "BusinessAccount")
    
    @classmethod
    def create_business_account(cls, user, address_obj:object, business_data:dict) -> CreateResult:
        allowed_keys = {
            "name", "email", "phone", "tagline",
            "industry", "niche", "bio",
        }
        
        if not allowed_keys.issubset(business_data.keys()):
            raise ValidationError("Missing required fields for BusinessAccount Model")

        business_acct, created = cls.BusinessAccounts.objects.get_or_create(
            owner=user,
            defaults={
                "business_name": business_data.get("name"),
                "business_email": business_data.get("email"),
                "business_phone": business_data.get("phone"),
                "tagline": business_data.get("tagline"),
                "industry": business_data.get("industry"),
                "niche": business_data.get("niche"),
                "bio": business_data.get("bio"),
                "address": address_obj,
            },
        )
        return CreateResult(instance=business_acct, created=created)