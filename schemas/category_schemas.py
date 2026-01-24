from pydantic import BaseModel,Field,field_serializer
from typing import Optional
from config import settings
from uuid import UUID


class CategoryCreate(BaseModel):
    name:str = Field(...,min_length=3,max_length=20)
    description:Optional[str] = None
    
    
class CategoryResponse(BaseModel):
    id:UUID
    name:str
    description:Optional[str] = None
    image_url:Optional[str] = None
    @field_serializer("image_url")
    def serialize_image_url(self,image_url:Optional[str]) -> Optional[str]:
        if not image_url:
            return None
        
        return f"{settings.BASE_URL}{image_url}"
    
    class Config:
        from_attributes=True
    
class CategoryUpdate(BaseModel):
    name:Optional[str] = None
    description:Optional[str] = None
    image_url:Optional[str] = None