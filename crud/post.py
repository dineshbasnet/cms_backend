from models.models import Post,User
from schemas.posts_schemas import PostCreate,PostResponse,PostUpdate,PostStatusEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from fastapi import HTTPException,status
from typing import List
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from schemas.user_schemas import Roles
from schemas.tag_schemas import TagResponse
from models.models import Tag


#Function to create posts(common)
async def create_post(db:AsyncSession,current_user:User,post_data:PostCreate) -> PostResponse:
    """
    Create a new post with optional tags and attach to author.
    """
    tags = []
    #Fetch tags if provided
    if post_data.tags:
        result = await db.execute(select(Tag).where(Tag.id.in_(post_data.tags)))
        tags = result.scalars().all()
        
    if current_user.role == Roles.admin:
        status = PostStatusEnum.published
    else:
        status = PostStatusEnum.pending_review
    
    #Create post instance
    new_post = Post(
        title = post_data.title,
        description = post_data.description,
        content = post_data.content,
        category_id = post_data.category_id,
        author_id = current_user.id,
        image_url = post_data.image_url,
        status = status
    )
    new_post.tags = tags
    db.add(new_post)
    try:
        await db.commit()
        await db.refresh(new_post)
        await db.refresh(new_post, attribute_names=["tags"])

        
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid data or foreign key constraint failed: {e}")
    
    return new_post

#Functions for Admin
#Function to fetch all posts
async def get_all_posts(db:AsyncSession,current_user:User,skip:int = 0,limit:int = 20) -> List[Post]:
    #only admins can view all posts 
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can viewed all posts"
        )
    try:
        result = await db.execute(
            select(Post)
            .options(
                selectinload(Post.tags)
            )
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            
        )
        posts = result.scalars().all()
        return posts
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to fetch posts")



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

#Function to delete posts
async def delete_post(
    db:AsyncSession,
    post_id:UUID,
    current_user:User
) ->Post:
    post = await get_post(db,post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    # Only admin can delete posts
    if current_user.role != Roles.admin and post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
        
    post.status = PostStatusEnum.archived
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return post

async def update_post(
    db:AsyncSession,
    post_id:UUID,
    current_user:User,
    post_update:PostUpdate
):
    """Updates post's details"""
    #Get post to update
    post = await get_post(db,post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    # Only admins and author can update posts
    if current_user.role != Roles.admin and post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your are not allowed to update this post"
        )
        
    new_post = await update_post_attributes(post,post_update,current_user,db)
    
    #Save in database
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return new_post

async def update_post_attributes(
    post:Post,
    post_update:PostUpdate,
    current_user:User,
    db:AsyncSession
    
) -> Post:
    """
    Apply updates to post attributes with permission checks for certain fields
    """
    if post_update.title is not None:
        post.title = post_update.title

    if post_update.description is not None:
        post.description = post_update.description

    if post_update.content is not None:
        post.content = post_update.content
        
    #Category change(only admins)
    if post_update.category_id is not None:
        if current_user.role != Roles.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change post category"
            )
        post.category_id = post_update.category_id
        
    #Tags (admins and author)
    if post_update.tags is not None:
        result = await db.execute(
            select(Tag).where(Tag.id.in_(post_update.tags))
        )
        post.tags = result.scalars().all()
        
    return post


#Functions for author only
async def  get_all_author_posts(
    db:AsyncSession,
    current_user:User,
    skip:int = 0,
    limit:int = 100
) ->List[Post]:
    try:
        result = await db.execute(
            select(Post)
            .options(
                selectinload(Post.tags)
            )
            .order_by(Post.created_at.desc())
            .where(Post.author_id == current_user.id)
            .offset(skip)
            .limit(limit)
            
        )
        
        posts = result.scalars().all()
        return posts
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to fetch posts")


async def get_author_single_post(
    db:AsyncSession,
    post_id:UUID,
    current_user:User
) -> Post:
    if current_user.role != Roles.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only access to the author"
        )
    post = await db.execute(
        select(Post)
        .options(selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    return post.scalar_one_or_none()


#Function for normal users(read only)
async def get_all_published_posts(
    db:AsyncSession
) -> List[Post]:
    """Access only published posts"""
    
    try:
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.status == PostStatusEnum.published)
            .order_by(Post.created_at.desc())
        )
        
        posts = result.scalars().all()
        return posts
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch posts"
        )

    
async def get_single_published_post(
    db:AsyncSession,
    post_id:UUID
) -> Post:
    """Access only published posts"""
    
    post =await get_post(db,post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    try:
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.status == PostStatusEnum.published)
            .order_by(Post.created_at.desc())
        )
        
        post = result.scalar_one_or_none()
        return post
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch posts"
        )    
    
        
    
        


