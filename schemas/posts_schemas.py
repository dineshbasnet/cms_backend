from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import datetime
from uuid import UUID

class PostBase(BaseModel):
    title:str = Field(...,min_length=3,max_length=255)    
    description:Optional[str] = None
    content:str
    category_id:int
    
    
class PostCreate(PostBase):
    author_id:Optional[int] = None

    
class PostUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    content: Optional[str]
    image_url: Optional[str]
    category_id: Optional[int]
    tags: Optional[List[int]]
    
    
class PostResponse(PostBase):
    id:UUID
    author_id:int
    created_at:datetime
    updated_at:datetime
    tags: List[str] = []
    
    class Config:
        from_attributes = True
    