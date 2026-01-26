from crud.user import (create_user,get_users,get_user_by_email,update_user_attributes,update_user_image,
                       get_user_by_id,update_user,delete_user)
from db import get_db
from uuid import UUID
from typing import List, Optional
from utils.auth import get_current_user, get_current_active_user
from utils.security import generate_otp, generate_secure_token,hashed_password, verify_password
from sqlalchemy import select
from schemas.user_schemas import (
            UserCreate,UserResponse,Roles,MeUserResponse, AccountStatusEnum,PasswordResetRequest,
            OTPVerification, PasswordChange, UserUpdate)
from models.models import User
from fastapi import APIRouter,Depends,HTTPException,status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile,File,Path,Body
from utils.email import render_email_template,send_email_smtp_async
from utils.redis import store_in_redis,get_from_redis,delete_from_redis


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register",response_model=UserResponse)
async def create_new_user(user_data:UserCreate,db:AsyncSession = Depends(get_db)):
    #Create new user
    new_user = await create_user(db,user_data)
    
    #Send welcome email
    email_html = render_email_template(
        "register.html",
        {"user_name":user_data.username,"user_email":user_data.email,"user_role":"user"}
    )
    
    await send_email_smtp_async(
        recipient=user_data.email,
        subject="Welcome to My app",
        html_content=email_html
    )
    
    return new_user
    
#Password management routes
@router.post("/password/request-reset",status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    email_data:PasswordResetRequest,
    db:AsyncSession = Depends(get_db)
):
    """
    Request a password reset by sending an OTP
    """
    user = await get_user_by_email(db,email_data.email)
    if not user:
        # Return success anyway to prevent email enumeration
        return {"message": "An OTP has been sent"}
    
    #Generate and store otp
    otp = generate_otp()
    await store_in_redis(f"otp:{email_data.email}",otp,ttl=600) #10 minutes expiry
    
    #Send OTP via email
    email_html = render_email_template(
        "password_change_otp.html",
        {"otp":otp,"user_name":user.username}
    )
    
    await send_email_smtp_async(
        recipient=email_data.email,
        subject="Your Password Reset OTP",
        html_content=email_html
    )
    
    return {"message":"If the email exists, an OTP has been sent"}
    
    
@router.post("/password/validate-otp",status_code=status.HTTP_200_OK)
async def validate_otp(otp_data:OTPVerification):
    """
    Validate the OTP and return a reset token
    """
    stored_otp = await get_from_redis(f"otp:{otp_data.email}")
    
    if not stored_otp or stored_otp != otp_data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
        
    #Delete the OTP to prevent reuse
    await delete_from_redis(f"otp:{otp_data.email}")
    
    #Generate and store reset token
    reset_token = generate_secure_token()
    await store_in_redis(f"reset_token:{otp_data.email}",reset_token,ttl=900) #15 minutes expiry
    
    return {"reset_token":reset_token}


@router.post("/password/reset",status_code=status.HTTP_200_OK)
async def reset_password(
    password_data:PasswordChange,
    db:AsyncSession = Depends(get_db)
):
    """
    Reset a user's password using the reset token
    """
    
    #Validate reset token
    stored_token = await get_from_redis(f"reset_token:{password_data.email}")
    
    if not stored_token or stored_token != password_data.reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
        
    #Get user and update password
    user = await get_user_by_email(db,password_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    #Update password
    user.hash_password = hashed_password(password_data.new_password)
    db.add(user)
    await db.commit()
        
    #Delete reset token to prevent reuse
    await delete_from_redis(f"reset_token:{password_data.email}")
    
    #Send confirmation email
    email_html = render_email_template(
        "password_change_confirmation.html",
        {"user_name":user.username}
        
    )
    
    await send_email_smtp_async(
        recipient=user.email,
        subject="Your Password has been changed",
        html_content=email_html
        
    )
    
    return {"message":"Password has been reset successfully"}

@router.post("/password/change",status_code=status.HTTP_200_OK)
async def change_password(
    current_password:str = Form(...),
    new_password:str = Form(...),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    """
    Change the password of the authenticated user
    """
    #Verify current password
    if not verify_password(current_password,current_user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
        
    #Update password
    current_user.hash_password = hashed_password(new_password)
    db.add(current_user)
    await db.commit()
        
        
    # Send confirmation email
    email_html = render_email_template(
        "password_change_confirmation.html", 
        {"user_name": current_user.username}
    )
    await send_email_smtp_async(
        recipient=current_user.email,
        subject="Your Password Has Been Changed",
        html_content=email_html
    )
    
    return {"message": "Password changed successfully"}
    
#User profile routes
@router.get("/me",response_model=UserResponse)
async def get_user_profile(current_user:User = Depends(get_current_active_user)):
    """Get the profile of authenticated user"""
    return current_user

@router.put("/me",response_model=UserResponse)
async def update_user_profile(
    user_update:UserUpdate,
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    """Update the profile of authenticated user"""
    update_user = await update_user_attributes(current_user,user_update,current_user,db)
    db.add(update_user)
    await db.commit()
    await db.refresh(update_user)

    return update_user

@router.post("/me/image",status_code=status.HTTP_200_OK)
async def upload_profile_picture(
    file:UploadFile = File(...),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
):
    """
    Upload or update profile picture for authenticated user
    """
    updated_user = await update_user_image(db,current_user,file)
    return {"message":"Profile image updated","image_url":updated_user.image_url}

        
# Admin routes for user management
@router.get("/",response_model=List[UserResponse])
async def get_all_users(
    skip:int = 0,
    limit:int = 100,
    role:Optional[Roles] = None,
    statuss:Optional[AccountStatusEnum] = None,
    current_user:User = Depends(get_current_active_user),
    db:AsyncSession = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can list all users"
        )
    filters = {
        "role":role,
        "status":statuss
    }
    
    users = await get_users(db,skip,limit,filters)
    return users


@router.get("/{user_id}",response_model=MeUserResponse)
async def get_user_by_id_route(
    user_id:UUID = Path(...,title="The id of user to get"),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
    
):
    """
    Get a specific user by ID (admin only or self)
    """
    #Self access or admin access
    if current_user.id != user_id and current_user.role != Roles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information"
        )
        
    user = await get_user_by_id(db,user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user


@router.put("/{user_id}",response_model=UserResponse)
async def update_user_route(
    user_id:UUID = Path(...,title="The Id of the user to update"),
    user_update:UserUpdate = Body(...),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
    
):
    """
    Update a specific user (admin only or self)
    """
    
    return await update_user(db,user_id,user_update,current_user)


@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    user_id:UUID = Path(...,title="The Id of user to delete"),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)
    
):
    """
    Delete a user (admin only or self)
    """
    await delete_user(db,user_id,current_user)
    return None


#verification routes
@router.post("/{user_id}/verify",status_code=status.HTTP_200_OK)
async def verify_user(
    user_id:UUID = Path(...,title="The Id of user to verify"),
    db:AsyncSession = Depends(get_db),
    current_user:User = Depends(get_current_active_user)

):
    """
    Verify a user (admin only)
    """
    if current_user.role != Roles.admin:
        raise HTTPException(
            status_code=403,
            detail="Only administrator can verify users"
        )
        
    user = await get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    user.verified = True
    user.status = AccountStatusEnum.active
    
    db.add(user)
    await db.commit()
    
    #Send verification confirmation email
    email_html = render_email_template(
        "account_verified.html",
        {"user_name":user.username}
    )

    await send_email_smtp_async(
        recipient=user.email,
        subject="Your account has been verified",
        html_content=email_html
    )
    
    return {"message":"User verified successfully","user_id":user.id}

