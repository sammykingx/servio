from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
import phonenumbers, pycountry
from phonenumbers.phonenumberutil import NumberParseException


POSTAL_REGEX = {
    "US": r"^\d{5}(-\d{4})?$",
    "CA": r"^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$",
    "GB": r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",
    "NG": r"^\d{6}$",
}

class UserProfileUpdatePayload(BaseModel):
    headline: str = Field(..., max_length=45, description="Professional headline shown on public profile")
    bio: str = Field(..., max_length=550, description="Professional bio shown on public profile")
    mobile_number: str = Field(..., max_length=18, description="Primary mobile number")
    alternate_number: Optional[str] = Field(None, max_length=15, description="Alternative mobile number (optional)")
    
    # @field_validator("mobile_number", "alternate_number")
    # @classmethod
    # def validate_mobile_number(cls, value):
    #     if value is None:
    #         return value
        
    #     try:
    #         phone = phonenumbers.parse(value, None)
    #     except NumberParseException:
    #         raise ValueError("Invalid phone number format or missing country code")

    #     if not phonenumbers.is_valid_number(phone):
    #         raise ValueError("Invalid phone number")

    #     if phonenumbers.number_type(phone) != phonenumbers.PhoneNumberType.MOBILE:
    #         raise ValueError("Number must be a mobile number")

    #     return phonenumbers.format_number(
    #         phone, phonenumbers.PhoneNumberFormat.E164
    #     )
        
    @field_validator("bio")
    @classmethod
    def validate_bio(cls, value):
        if len(value.split(" ")) > 60:
            raise ValueError("Bio should not be more than 60 words")
        
        return value
    
    
class UserAddressUpdatePayload(BaseModel):
    street: str = Field(..., max_length=50, description="Street address")
    street_line_2: Optional[str] = Field(None, max_length=50, description="Additional address line (optional)")
    city: str = Field(..., max_length=17, description="City")
    province: str = Field(..., max_length=17, description="Province/State")
    country: Optional[str] = Field(None, max_length=65)
    postal_code: str = Field(..., max_length=10, description="Postal code")


    @field_validator("country")
    @classmethod
    def validate_country(cls, value):
        if value is None:
            return value
        if not pycountry.countries.get(name=value) and not pycountry.countries.get(alpha_2=value):
            raise ValueError("Hmm, we don’t recognize that country. Please double-check and try again.")
        return value
    
    @field_validator("province")
    @classmethod
    def validate_province(cls, value, values):
        country = values.data.get("country")
        if country is None:
            return value
        country_obj = pycountry.countries.get(name=country) or pycountry.countries.get(alpha_2=country)
        if country_obj:
            valid_states = [s.name for s in pycountry.subdivisions.get(country_code=country_obj.alpha_2)]
            if value not in valid_states:
                raise ValueError(f"{value} is not a valid province/state for {country}")
        return value

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, value, values):
        country = values.data.get("country")
        if not country:
            return value  # cannot validate without country
        country_obj = pycountry.countries.get(name=country) or pycountry.countries.get(alpha_2=country)
        if country_obj and country_obj.alpha_2 in POSTAL_REGEX:
            import re
            pattern = POSTAL_REGEX[country_obj.alpha_2]
            if not re.match(pattern, value):
                raise ValueError(f"Invalid postal code for {country}")
        return value