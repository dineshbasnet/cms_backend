from models.models import Post
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from fastapi import HTTPException,status
from typing import List
from sqlalchemy import select


#Function to create posts
async def create_post(db:AsyncSession,post:PostCreate) -> PostResponse:
    
    new_post = Post(
        title = post.title,
        description = post.description,
        content = post.content,
        category_id = post.category_id
    )
    db.add(new_post)
    try:
        await db.commit()
        await db.refresh(new_post)
        await db.refresh(new_post, attribute_names=["tags"])

        
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid data or foreign key constraint failed: {e}")
    
    return new_post



#Function to fetch all posts
async def get_all_posts(db:AsyncSession) -> List[PostResponse]:
    try:
        result = await db.execute(select(Post))
        posts = result.scalars().all()
        return posts
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to fetch categories")



#Function to fetch single posts
async def get_post(db:AsyncSession,post_id:int) -> PostResponse:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    return post
    