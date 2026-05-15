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


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class AnswerResponse(BaseModel):
    answer: str
    sources: list[dict]
