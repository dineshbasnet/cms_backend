# FastAPI Blog Management System

A modern **CMS/Blog Management System** built with **FastAPI**, **Async SQLAlchemy**, **PostgreSQL**, **Redis**, and **JWT authentication**.  
This project supports **role-based access**, **post management**, **user registration**, **password reset with OTP**, and **email notifications**.

## Features

### User Management
- **Roles:** Admin, Author, User
- **Account statuses:** Active, Inactive, Suspended, Deleted
- **Secure password hashing** using `argon2`
- **JWT-based authentication**
- Users can update their profile, change password, and request password resets.
- Admins can:
  - Promote users to authors
  - Suspend or delete users
  - Manage roles and statuses

### Blog/Post Management
- **Post statuses:** Draft, Published, Archived
- **Tag system:** Many-to-many relationship between posts and tags
- Authors can create, update, and view their own posts
- Admins can manage **all posts** regardless of status
- Users can view **published posts** only
- Soft delete and archive system for posts

### Categories
- Admin-only category creation, update, and deletion
- Posts are linked to categories
- Safe deletion with post relationship check

### OTP and Email
- Password reset with **OTP via email**
- Email templates using **Jinja2**
- Async SMTP email sending
- Redis used for OTP storage with expiration

### Security
- JWT token authentication for protected routes
- Role-based access control
- Status validation for users and posts
- Input validation with Pydantic schemas

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (async)
- **Caching / OTP:** Redis
- **Authentication:** JWT (PyJWT)
- **Password hashing:** Argon2
- **Async email:** aiosmtplib
- **Templates:** Jinja2
- **Migrations:** Alembic

