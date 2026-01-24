from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class TagCreate(BaseModel):
    name:str
    description:Optional[str] = None
    
    
class TagResponse(TagCreate):
    id:UUID

class TagUpdate(BaseModel):
    name:Optional[str] = None
    description:Optional[str] = None
    