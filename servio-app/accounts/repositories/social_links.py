from django.core.exceptions import ValidationError
from django.apps import apps
from accounts.models.socials import Platform

class SocialLinkRepository:
    SocialLink = apps.get_model("accounts", "SocialLink")

    @staticmethod
    def validate_owner_or_business(user=None, business=None):
        """
        Validates that either a user or a business is provided, but not both.
        Raises ValidationError if validation fails.
        """
        if not user and not business:
            raise ValidationError("Either 'user' or 'business' must be provided.")
        if user and business:
            raise ValidationError("Cannot provide both 'user' and 'business'.")
        return True

    @classmethod
    def get_filters(cls, user=None, business=None):
        """
        Validates and returns the filter dictionary for querying SocialLink.
        """
        cls.validate_owner_or_business(user=user, business=business)
        return {"user": user} if user else {"business": business}
    
    
    @classmethod
    def create_or_update_socials(cls, socials: dict, user=None, business=None):
        """
            Creates or updates social links for a user or business.
            - user: User instance (normal user)
            - business: BusinessAccount instance
            - socials: dict of platform_name -> url
        """
        platform_map = dict(Platform.choices)        
        filters = cls.get_filters(user=user, business=business)
        social_links = []
        print("creating links")
        for platform_name in platform_map.keys():
            url = socials.get(platform_name, None)
            if url:
                social_link, created = cls.SocialLink.objects.update_or_create(
                    **{**filters, "platform": platform_name},
                    defaults={"url": url},
                )
                social_links.append(
                    {
                        "platform": platform_name,
                        "url": url,
                        "created": created
                    }
                )
        print("Done: ", social_links)
        return social_links

    @classmethod
    def delete_business_social(cls, platform, user=None, business=None):
        """
        Deletes a social link for a business.
        """
        filters = cls.get_filters(user=user, business=business)
        cls.SocialLink.objects.filter(**filters, platform=platform).delete()

    @classmethod
    def list_business_socials(cls, user=None, business=None):
        """
        Returns all social links for a business.
        """
        filters = cls.get_filters(user=user, business=business)
        return cls.SocialLink.objects.filter(**filters).all()
