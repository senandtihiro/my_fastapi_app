# app/api/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dao.product_dao import ProductDAO
from app.dao.user_dao import UserDAO
from app.services.product_service import ProductService
from app.services.user_service import UserService


# 数据库会话依赖
DBSession = Annotated[AsyncSession, Depends(get_db)]


# Product Service依赖
async def get_product_service(db: DBSession) -> ProductService:
    product_dao = ProductDAO(db)
    return ProductService(product_dao)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]


# User Service依赖
async def get_user_service() -> UserService:
    user_dao = UserDAO()
    return UserService(user_dao)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]