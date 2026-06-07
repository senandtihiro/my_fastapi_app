# app/api/v1/products.py
from typing import List

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from app.schemas.product import ProductResponse, ProductQueryParams
from app.services.product_service import ProductService
from app.api.deps import ProductServiceDep
from app.core.logger import logger
from app.utils.response import success, ApiResponse
from app.exceptions.business_exceptions import api_handler
from app.schemas.product import ProductCreate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/add")
@api_handler
async def create_product(
        product_data: ProductCreate,
        product_service: ProductServiceDep = None
):
    """
    创建单个产品

    - **name**: 产品名称（必填，1-200字符）
    - **description**: 产品描述（可选，最多500字符）
    - **price**: 价格（必填，大于0）
    - **stock**: 库存（默认0，大于等于0）
    - **category**: 分类（可选）
    - **sku**: SKU编码（必填，唯一）

    示例请求:
    ```json
    {
        "name": "iPhone 15 Pro",
        "description": "苹果最新款手机",
        "price": 7999.00,
        "stock": 100,
        "category": "电子产品",
        "sku": "IPHONE15PRO-001"
    }
    """
    result = await product_service.create_product(product_data)
    return success(data=result, message="产品创建成功")



@router.get("/search")
@api_handler
async def search_products(
        name: str = Query(None, description="产品名称（模糊搜索）"),
        category: str = Query(None, description="分类"),
        min_price: float = Query(None, ge=0, description="最低价格"),
        max_price: float = Query(None, ge=0, description="最高价格"),
        skip: int = Query(0, ge=0, description="跳过数量"),
        limit: int = Query(10, ge=1, le=100, description="每页数量"),
        product_service: ProductServiceDep = None
):
    """
    搜索产品接口（从MySQL查询）

    - **name**: 产品名称模糊搜索
    - **category**: 按分类筛选
    - **min_price**: 最低价格
    - **max_price**: 最高价格
    - **skip**: 分页跳过数量
    - **limit**: 每页返回数量
    """
    products = await product_service.search_products(
        name=name,
        category=category,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit
    )
    logger.info(f"Product search completed, found {len(products)} products")
    return success(data=products)
