from pydantic import BaseModel, Field, model_validator


class PasswordChangeSchema(BaseModel):
    """
    A unified schema for password updates and resets.
    
    Validates that the provided passwords meet length requirements 
    and are identical before proceeding with the change.
    """
    
    password1: str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)
    auto_login: bool = False
    
    @model_validator(mode="after")
    def validate_passwords(self) -> 'PasswordChangeSchema':
        if self.password1 != self.password2:
            raise ValueError("Password confirmation does not match the provided password.")
        return self