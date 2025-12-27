from db import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Table
from sqlalchemy.orm import relationship
from datetime import datetime,timezone


#user model for cms system
class User(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,nullable=False,unique=True)
    email = Column(String,nullable=False)
    phone = Column(String,nullable=True)
    hash_password = Column(String,nullable=False)
    image_url = Column(String)
    posts = relationship('Post',back_populates='author')
    comments = relationship('Comment',back_populates='user')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)




#category model for cms system
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    description = Column(String,nullable=True)
    image_url = Column(String,nullable=True)
    posts = relationship('Post',back_populates='category')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
#tags model for cms system
class Tag(Base):
    __tablename__="tags"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    description = Column(String,nullable=True)
    posts = relationship('Post',secondary='post_tags',back_populates='tags')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
     
    
#post model for cms system
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    description = Column(String,nullable=True)
    content = Column(String,nullable=False)
    image_url = Column(String)
    author_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    category_id = Column(Integer,ForeignKey('categories.id'),nullable=False)
    author = relationship('User',back_populates='posts')
    category = relationship('Category',back_populates='posts')
    comments = relationship('Comment',back_populates='posts')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship('Tag',secondary='post_tags',back_populates='posts')
    
    
class Comment(Base):
    __tablename__="comments"
    id = Column(Integer,primary_key=True)
    post_id = Column(Integer,ForeignKey('posts.id'),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    message = Column(String,nullable=False)
    posts = relationship('Post',back_populates='comments')
    user = relationship('User',back_populates='comments')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id',Integer,ForeignKey('posts.id'),primary_key=True),
    Column('tag_id',Integer,ForeignKey('tags.id'),primary_key = True)
    
)

        