from pydantic import BaseModel, Field
from typing import Literal
class RegisterRequest(BaseModel):
    login_id: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=72)
    emp_name: str = Field(min_length=1, max_length=30)
    emp_age: int = Field(ge=18, le=60)
    emp_gender: Literal["Male", "Female"]
    emp_branch: str = Field(min_length=1, max_length=30)

class LoginRequest(BaseModel):
    login_id: str
    password: str
class TokenResponse(BaseModel):
    access_token: str
    token_type: str