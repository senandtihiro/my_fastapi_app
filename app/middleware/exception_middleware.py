# app/middleware/exception_middleware.py
# 不导入 success/error，保持独立
from fastapi.responses import JSONResponse
# app/middleware/exception_middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable
from app.core.logger import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        处理请求的中间件方法

        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理函数

        Returns:
            响应对象
        """
        try:
            # 正常处理请求
            return await call_next(request)

        except RequestValidationError as e:
            # 处理请求参数验证错误
            logger.warning(f"Request validation error: {e.errors()}")

            # 格式化错误信息
            errors = []
            for err in e.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                errors.append(f"{field}: {err['msg']}")

            return JSONResponse(
                status_code=422,
                content={
                    "code": 2,
                    "message": "请求参数验证失败",
                    "data": {"errors": errors}
                }
            )

        except StarletteHTTPException as e:
            # 处理HTTP异常（404, 401, 403等）
            logger.warning(f"HTTP exception: {e.status_code} - {e.detail}")

            # 根据状态码映射错误码
            error_code = e.status_code
            if e.status_code == 404:
                error_code = 3
            elif e.status_code == 401:
                error_code = 4
            elif e.status_code == 403:
                error_code = 5
            elif e.status_code == 409:
                error_code = 6

            return JSONResponse(
                status_code=e.status_code,
                content={
                    "code": error_code,
                    "message": e.detail,
                    "data": None
                }
            )

        except Exception as e:
            # 处理未预期的系统异常
            logger.exception(f"Unhandled exception: {str(e)}")

            # 获取调试模式配置
            debug = getattr(request.app, "debug", False)

            return JSONResponse(
                status_code=500,
                content={
                    "code": 1,
                    "message": "服务器内部错误，请稍后重试",
                    "data": None if not debug else {"detail": str(e)}
                }
            )


def setup_exception_handlers(app):
    """设置全局异常处理器"""
    app.add_middleware(ExceptionHandlerMiddleware)
