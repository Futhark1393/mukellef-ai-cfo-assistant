from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=128)
    tenant_slug: str = Field(min_length=2, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="owner", max_length=32)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
