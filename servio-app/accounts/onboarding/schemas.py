# schemas used for onboarding flows

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
import html, re


SCRIPT_RE = re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.I | re.S)

def sanitize_text(value: str) -> str:
    value = html.escape(value)
    value = SCRIPT_RE.sub("", value)
    value = re.sub(r"[<>]", "", value)  # hard strip
    return value.strip()

class AddressPayload(BaseModel):
    street: str = Field(..., min_length=5, max_length=120)
    street_line_two: Optional[str] = Field(default=None, max_length=100)
    city: str = Field(..., min_length=3, max_length=18)
    state: str = Field(..., min_length=3, max_length=18)
    postal_code: str = Field(..., min_length=3, max_length=7)
    country: str = Field(..., min_length=3, max_length=25)
    
    @field_validator(
        "street",
        "street_line_two",
        "city",
        "state",
        "country",
        "postal_code",
        mode="before",
    )
    @classmethod
    def clean_text(cls, v, field):
        if v is None:
            return v
        v = sanitize_text(v)
        if field.field_name == "street_line_two":
            return None
        if not v:
            raise ValueError("Field cannot be empty")
        return v
    
class NumberPayload(BaseModel):
    phoneCountryCode: str = Field(..., min_length=2, max_length=4)
    phoneNumber: str = Field(..., max_length=12)
    altNumber: Optional[str] = Field(..., max_length=16)
    
class ProfilePayLoad(BaseModel):
    profile: NumberPayload
    address: AddressPayload
    
class ExperienceLevel(str, Enum):
    ZERO_TO_TWO = "0-2"
    THREE_TO_FIVE = "3-5"
    FIVE_TO_TEN = "5-10"
    TEN_PLUS = "10+"
 
class IdName(BaseModel):
    id: int
    name: str

class OnboardingStepTwoPayload(BaseModel):
    industry: IdName
    experience_level: ExperienceLevel
    bio: str = Field(..., max_length=400)
    niches: List[IdName]

    @field_validator("bio", mode="after")
    @classmethod
    def validate_bio(cls, value:str):
        value = sanitize_text(value).strip()
        if len(value.split()) > 30:
            raise ValueError("Bio should not be more than 30 words")
        return value


class OnboardingIntentOptions(str, Enum):
    BOOK_SERVICES = "book_services"
    CREATE_GIGS = "create_gigs"
    COLLABORATE = "collaborate"
    
class OnboardingIntents(BaseModel):
    intents: List[OnboardingIntentOptions]