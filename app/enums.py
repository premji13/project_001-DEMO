from enum import Enum

class UserType(str, Enum):
    """User type enumeration"""
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    GUEST = "GUEST"