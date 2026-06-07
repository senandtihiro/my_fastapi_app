# app/exceptions/business_exceptions.py
from typing import Any, Optional


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(
            self,
            message: str,
            code: int = 1,
            data: Any = None
    ):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, message: str = "资源不存在", data: Any = None):
        super().__init__(message, code=3, data=data)


class ValidationException(BusinessException):
    """数据验证异常"""

    def __init__(self, message: str = "数据验证失败", data: Any = None):
        super().__init__(message, code=2, data=data)


class DatabaseException(BusinessException):
    """数据库异常"""

    def __init__(self, message: str = "数据库操作失败", data: Any = None):
        super().__init__(message, code=7, data=data)


# app/decorators/business_decorator.py
import functools
import inspect
from typing import Callable, Type, Union, Tuple, Optional, Any
from fastapi import HTTPException
from app.utils.response import error, success
from app.exceptions.business_exceptions import BusinessException
from app.core.logger import logger


def handle_business_exception(
        default_message: str = "操作失败",
        log_error: bool = True,
        return_error_response: bool = True,
        catch_exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = BusinessException
):
    """
    业务异常处理装饰器

    Args:
        default_message: 默认错误消息
        log_error: 是否记录错误日志
        return_error_response: 是否返回错误响应（False则重新抛出异常）
        catch_exceptions: 要捕获的异常类型

    Example:
        @router.get("/products/{id}")
        @handle_business_exception()
        async def get_product(id: int, service: ProductServiceDep):
            product = await service.get_product(id)
            if not product:
                raise NotFoundException(f"产品{id}不存在")
            return success(data=product)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # 执行原函数
                print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                result = await func(*args, **kwargs)
                return result

            except catch_exceptions as e:
                # 处理业务异常
                if log_error:
                    logger.warning(
                        f"Business exception in {func.__name__}: {e.message}",
                        extra={"error_code": e.code, "error_data": e.data}
                    )

                if return_error_response:
                    # 返回错误响应
                    return error(
                        message=e.message,
                        code=e.code,
                        data=e.data
                    )
                else:
                    # 重新抛出异常
                    raise

            except Exception as e:
                # 处理未预期的异常
                if log_error:
                    logger.error(
                        f"Unexpected error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )

                if return_error_response:
                    return error(
                        message=default_message,
                        code=1,
                        data={"detail": str(e)}
                    )
                else:
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except catch_exceptions as e:
                if log_error:
                    logger.warning(f"Business exception in {func.__name__}: {e.message}")

                if return_error_response:
                    return error(message=e.message, code=e.code, data=e.data)
                else:
                    raise
            except Exception as e:
                if log_error:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)

                if return_error_response:
                    return error(message=default_message, code=1)
                else:
                    raise

        # 判断是异步函数还是同步函数
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator


# 预定义的装饰器
def api_handler(func: Callable) -> Callable:
    """API处理器装饰器 - 自动处理业务异常并返回统一格式"""
    return handle_business_exception(
        default_message="请求处理失败",
        log_error=True,
        return_error_response=True
    )(func)
