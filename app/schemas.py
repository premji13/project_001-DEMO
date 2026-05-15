from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.enums import UserType

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    user_type: UserType
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

class VerificationResponse(BaseModel):
    message: str
    user: UserResponse

