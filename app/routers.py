from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.database import get_db
from app.crud import get_user_by_email, create_user
from app.security import verify_password, create_access_token, hash_password
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.email import send_otp_email

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user and send OTP to email.
    """
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = create_user(db, user=user)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Send OTP email
    # Note: In a real app, you might want to handle email failure more gracefully
    # For now, we'll send it synchronously and fail if email doesn't work
    from app.crud import get_latest_otp
    otp_record = get_latest_otp(db, new_user.id)
    
    if otp_record:
        email_sent = send_otp_email(
            to_email=new_user.email,
            otp=otp_record.otp,
            username=new_user.username
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email. Please try again."
            )
    
    return new_user

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    """
    db_user = get_user_by_email(db, email=user.email)
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get current user from token.
    """
    from app.security import verify_token
    
    email = verify_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

