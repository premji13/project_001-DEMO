import random
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import User, EmailOTP
from app.schemas import UserRegister
from app.security import hash_password
from app.enums import UserType
from datetime import datetime, timedelta


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserRegister) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        user_type=UserType.USER
    )
    db.add(db_user)
    try:
        db.flush()
        
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        otp_user = EmailOTP(
            user_id=db_user.id,
            otp=otp,
            expires_at=expires_at
        )
        db.add(otp_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None

def get_latest_otp(db: Session, user_id: int) -> EmailOTP:
    return db.query(EmailOTP).filter(
        EmailOTP.user_id == user_id
    ).order_by(EmailOTP.created_at.desc()).first()

def verify_otp(db: Session, user_id: int, otp: str) -> bool:
    email_otp = get_latest_otp(db, user_id)
    if not email_otp:
        return False
    
    if datetime.utcnow() > email_otp.expires_at:
        return False
    
    return email_otp.otp == otp

def delete_user_otps(db: Session, user_id: int):
    db.query(EmailOTP).filter(EmailOTP.user_id == user_id).delete()
    db.commit()

def mark_user_verified(db: Session, user_id: int) -> User:
    user = get_user_by_id(db, user_id)
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)
    return user

