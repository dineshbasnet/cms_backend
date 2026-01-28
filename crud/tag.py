from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.tag_schemas import TagCreate,TagResponse,TagUpdate
from models.models import Tag, User,Post
from typing import List
from uuid import UUID
from fastapi import HTTPException,status
from sqlalchemy.future import select
from schemas.user_schemas import Roles
from sqlalchemy.exc import IntegrityError



#Function to create tags
async def create_tags(db:AsyncSession,tag_data:TagCreate,current_user:User) -> Tag:
    
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tags"
        )
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Tag already exists")
    
    return new_tags
    

async def get_all_tags(
    db:AsyncSession
) -> List[Tag]:
    """Only admin and author can access all tags"""
    try:
        result = await db.execute(select(Tag).order_by(Tag.created_at.desc()))
        tags = result.scalars().all()
        return tags
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch tags")
    

async def get_single_tag(
    db:AsyncSession,
    tag_id:UUID
) -> Tag:
    try:
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
            
        return tag
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch tag"
        )

    

async def delete_tags(
    db:AsyncSession,
    tag_id:UUID
):
    """Only admin can delete tags"""
    tag = await get_single_tag(db,tag_id)
    
    posts_count = await db.execute(
        select(Post).join(Post.tags).where(Tag.id == tag_id)
    )
    
    if posts_count.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete tag: It is associated with posts"
        )
        
    await db.delete(tag)
    await db.commit()
    return {"detail":"Tag deleted"}