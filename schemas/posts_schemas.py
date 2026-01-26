from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import datetime
from uuid import UUID
from enum import Enum
from .tag_schemas import TagResponse

class PostStatusEnum(str, Enum):
    draft = "draft"                
    published = "published"        
    archived = "archived"          
    pending_review = "pending_review" 
    
    
class PostBase(BaseModel):
    title:str = Field(...,min_length=3,max_length=255)    
    description:Optional[str] = None
    content:str
    category_id:UUID
    image_url:Optional[str] = None
    tags:Optional[List[UUID]] = []
    
    
class PostCreate(PostBase):
    status:Optional[PostStatusEnum] = None
    
    class Config:
        from_attributes = True

    
class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[UUID]] = None
    
    
class PostResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    content: str
    image_url: Optional[str]
    author_id: UUID
    category_id: UUID
    tags: List[TagResponse] = []
    created_at: datetime
    updated_at: datetime
    status:PostStatusEnum
    created_at:datetime
    updated_at:datetime
    
    class Config:
        from_attributes = True
    

class PostStatusUpdate(BaseModel):
    status:PostStatusEnum