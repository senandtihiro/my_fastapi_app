# app/schemas/product.py
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """创建产品请求模型"""
    name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    description: Optional[str] = Field(None, max_length=500, description="产品描述")
    price: float = Field(..., gt=0, description="价格")
    stock: int = Field(0, ge=0, description="库存")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    sku: str = Field(..., min_length=1, max_length=100, description="SKU编码")

    @validator('sku')
    def validate_sku(cls, v):
        """验证SKU格式"""
        if not v.isalnum() and '-' not in v:
            raise ValueError('SKU只能包含字母、数字和连字符')
        return v.upper()

    @validator('price')
    def validate_price(cls, v):
        """验证价格"""
        if v <= 0:
            raise ValueError('价格必须大于0')
        return round(v, 2)


class ProductResponse(BaseModel):
    """产品响应Schema"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    sku: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductQueryParams(BaseModel):
    """产品查询参数"""
    name: Optional[str] = Field(None, description="产品名称")
    category: Optional[str] = Field(None, description="分类")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(10, ge=1, le=100, description="每页数量")
