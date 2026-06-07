# app/schemas/user.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """用户响应Schema"""
    user_id: str
    username: str
    email: str
    age: Optional[int] = None
    city: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)