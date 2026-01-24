from pydantic import BaseModel,EmailStr,Field,field_serializer
from typing import Optional
from config import settings
from uuid import UUID

class UserCreate(BaseModel):
    username:str = Field(...,min_length=2,max_length=30)
    email:EmailStr
    phone:str = Field(...,min_length=8,max_length=10)
    password:str = Field(...,min_length=8)
    

class UserResponse(BaseModel):
    id:UUID
    username:str
    email:EmailStr
    phone:Optional[str] = None
    image_url:Optional[str] = None
    @field_serializer("image_url")
    def serialize_image_url(self,image_url:Optional[str]) -> Optional[str]:
        if not image_url:
            return None
        
        return f"{settings.BASE_URL}{image_url}"
    
    class Config:
        from_attributes=True
        
# for user update model for cms
class UserUpdate(BaseModel):
    username:Optional[str]
    email:Optional[EmailStr]
    phone:Optional[str]
    image_url:Optional[str]
    password:Optional[str]
    