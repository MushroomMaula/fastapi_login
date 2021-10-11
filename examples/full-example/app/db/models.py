from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(80))
    is_admin = Column(Boolean, default=False)
    posts = relationship("Posts", back_populates="owner")


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    owner = relationship("User", back_populates="posts")
    created_at = Column(DateTime, server_default=func.now())