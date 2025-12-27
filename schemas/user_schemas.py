from pydantic import BaseModel,EmailStr,Field
from typing import Optional

class UserCreate(BaseModel):
    username:str = Field(...,min_length=2,max_length=30)
    email:EmailStr
    phone:str = Field(...,min_length=8,max_length=10)
    password:str = Field(...,min_length=8)
    

class UserResponse(BaseModel):
    id:int
    username:str
    email:EmailStr
    phone:Optional[str] = None
    image_url:Optional[str] = None
    
    class Config:
        orm_mode=True
        
# for user update model for cms
class UserUpdate(BaseModel):
    username:str = Field(...,min_length=2,max_length=30)
    email:EmailStr
    password:str = Field(...,min_length=8)
    