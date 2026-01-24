from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.tag_schemas import TagCreate,TagResponse,TagUpdate
from models.models import Tag
from fastapi import HTTPException,status
from sqlalchemy.exc import IntegrityError,SQLAlchemyError



#Function to create tags
async def create_tags(db:AsyncSession,tag_data:TagCreate) -> TagResponse:
    new_tags = Tag(
        name = tag_data.name,
        description = tag_data.description
    )
    db.add(new_tags)
    
    try:
        await db.commit()
        await db.refresh(new_tags)
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid data")
    
    return new_tags
    