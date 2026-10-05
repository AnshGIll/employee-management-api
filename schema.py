from pydantic import BaseModel
class RegisterRequest(BaseModel):
    login_id: str
    password: str
    emp_name: str
    emp_age: int
    emp_gender: str
    emp_branch: str
class LoginRequest(BaseModel):
    login_id: str
    password: str
class TokenResponse(BaseModel):
    access_token: str
    token_type: str