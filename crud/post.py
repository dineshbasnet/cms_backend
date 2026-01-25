from models.models import Post
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from fastapi import HTTPException,status
from typing import List
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from schemas.tag_schemas import TagResponse
from models.models import Tag


#Function to create posts
async def create_post(db:AsyncSession,author_id:UUID,post:PostCreate) -> PostResponse:
    tags = []
    if post.tags:
        result = await db.execute(select(Tag).where(Tag.id.in_(post.tags)))
        tags = result.scalars().all()
    
    new_post = Post(
        title = post.title,
        description = post.description,
        content = post.content,
        category_id = post.category_id,
        author_id = author_id,
        tags = tags,
        image_url = post.image_url
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
async def get_all_posts(db:AsyncSession,skip:int = 0,limit:int = 20) -> List[PostResponse]:
    try:
        result = await db.execute(
            select(Post)
            .options(
                selectinload(Post.tags)
            )
            .offset(skip)
            .limit(limit)
            
        )
        posts = result.scalars().all()
        return posts
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to fetch categories")



#Function to fetch single posts
async def get_post(db:AsyncSession,post_id:int) -> PostResponse:
    result = await db.execute(select(Post).options(selectinload(Post.tags)).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    return post


#Function to update posts
async def update_post(db:AsyncSession,update_data:PostUpdate,post_id:UUID) -> PostResponse:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    
    post = result.scalars().first()
    
    if not post:
        return None
    
    for field, value in update_data.dict(exclude_unset=True).items():
        if field != "tags":
            setattr(post,field,value)
            
    if update_data.tags is not None:
        tags_result = await db.execute(
            select(Tag).where(Tag.id.in_(update_data.tags))
        )
        post.tags = tags_result.scalars().all()
    
    await db.commit()
    await db.refresh(post)

    return PostResponse(
        id=post.id,
        title=post.title,
        description=post.description,
        content=post.content,
        image_url=post.image_url,
        author_id=post.author_id,
        category_id=post.category_id,
        tags=[TagResponse.from_orm(tag) for tag in post.tags],
        created_at=post.created_at,
        updated_at=post.updated_at
    )



    


    