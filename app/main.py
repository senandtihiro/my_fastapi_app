# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.core.elasticsearch_client import es_client
from app.middleware.exception_middleware import setup_exception_handlers
from app.api import product
from app.api import user
from app.core.database import engine as aync_engine
from app.core.database import Base
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting application...")
    print('开始创建数据表...')
    async with aync_engine.begin() as conn:
        # run_sync 用于在异步上下文中执行同步的建表操作
        await conn.run_sync(Base.metadata.create_all)

    # 连接Elasticsearch
    # await es_client.connect()
    logger.info("Elasticsearch connected")

    yield

    # 关闭Elasticsearch
    logger.info("Shutting down...")
    # await es_client.close()
    logger.info("Elasticsearch disconnected")


async def create_tables():
    print('create tables')
    async with aync_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all())






def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 设置异常处理
    setup_exception_handlers(app)

    # 注册路由
    app.include_router(product.router, prefix="/api/v1")
    app.include_router(user.router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "endpoints": {
                "products": "/api/v1/products",
                "users": "/api/v1/users"
            }
        }


    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_application()


# @app.on_event("startup")
# async def startup_event():
#     await create_tables()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )