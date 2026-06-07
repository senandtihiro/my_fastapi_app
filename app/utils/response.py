# app/utils/response.py
from fastapi.responses import JSONResponse
# from app.schemas.common import ApiResponse
# app/schemas/common.py
from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel):
    """统一API响应格式 - 简化版"""
    code: int = Field(..., description="状态码，0表示成功，非0表示失败")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "操作成功",
                "data": {"id": 1, "name": "示例"}
            }
        }


def success(data=None, message="操作成功", code=0):
    """业务层使用"""
    return ApiResponse(code=code, message=message, data=data)


def error(message="操作失败", code=1, data=None):
    """业务层使用"""
    return ApiResponse(code=code, message=message, data=data)


def json_response(response: ApiResponse, status_code: int = 200) -> JSONResponse:
    """将 ApiResponse 转换为 JSONResponse（中间件使用）"""
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )


# 中间件中使用
class ExceptionHandlerMiddleware:
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # 使用专门的转换函数
            return json_response(
                error(message="服务器错误", code=1),
                status_code=500
            )
