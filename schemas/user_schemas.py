from pydantic import BaseModel,EmailStr,Field,field_serializer, validator
from typing import Optional,Literal
from config import settings
from enum import Enum
from uuid import UUID
from datetime import datetime

class AccountStatusEnum(str,Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    deleted = "deleted"
    pending_verification = "pending_verification"

class UserCreate(BaseModel):
    username:str = Field(...,min_length=2,max_length=30)
    email:EmailStr
    phone:str = Field(...,min_length=8,max_length=10)
    password:str = Field(...,min_length=8)
    
    
class Roles(str,Enum):
    user = "user"
    admin = "admin"
    author = "author"
    

class UserResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    role:Roles
    status:AccountStatusEnum
    image_url:Optional[str] = None
    created_at:datetime
    @field_serializer("image_url")
    def serialize_image_url(self,image_url:Optional[str]) -> Optional[str]:
        if not image_url:
            return None
        
        return f"{settings.BASE_URL}{image_url}"
    
    class Config:
        from_attributes=True
        
class MeUserResponse(UserResponse):
    phone:Optional[str] = None
    last_login:Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
        
# for user update model for cms
class UserUpdate(BaseModel):
    username:Optional[str] = None
    email:Optional[EmailStr] = None
    phone:Optional[str] = None
    image_url:Optional[str] = None
    password:Optional[str] = None
    status:Optional[AccountStatusEnum] = None
    verified:Optional[bool] = None
    role:Optional[Roles] = None
    
    @validator('username')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v
        
    @validator('password')
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    
class PasswordResetRequest(BaseModel):
    email:EmailStr
    
    
class PasswordChange(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str = Field(..., min_length=8)


class OTPVerification(BaseModel):
    email: EmailStr
    otp: str
    
    
class UserRoleUpdate(BaseModel):
    role:Literal[Roles.admin,Roles.author,Roles.user]