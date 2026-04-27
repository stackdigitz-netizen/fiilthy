"""
Error Handling & Logging System
Comprehensive error handling and production logging
"""

import logging
import traceback
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
from functools import wraps
from pathlib import Path


DEFAULT_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
SERVERLESS_LOGS_DIR = Path("/tmp/fiilthy-logs")


def resolve_logs_dir() -> Path:
    candidate = SERVERLESS_LOGS_DIR if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) else DEFAULT_LOGS_DIR
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    except OSError:
        SERVERLESS_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        return SERVERLESS_LOGS_DIR


LOGS_DIR = resolve_logs_dir()


class ProductionLogger:
    """Production-grade logging system"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        if self.logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)

        try:
            file_handler = logging.FileHandler(LOGS_DIR / f"{name}.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except OSError:
            self.logger.warning("File logging unavailable; using stdout only")
    
    def info(self, message: str, **kwargs):
        self.logger.info(f"{message} | {json.dumps(kwargs)}")
    
    def error(self, message: str, error: Exception = None, **kwargs):
        if error:
            self.logger.error(f"{message} | {str(error)} | {json.dumps(kwargs)}")
            self.logger.debug(traceback.format_exc())
        else:
            self.logger.error(f"{message} | {json.dumps(kwargs)}")
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(f"{message} | {json.dumps(kwargs)}")
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(f"{message} | {json.dumps(kwargs)}")


class ErrorResponse:
    """Standard error response format"""
    
    @staticmethod
    def format_error(
        error: Exception,
        status_code: int = 500,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format error for API response"""
        return {
            "success": False,
            "error": {
                "message": message,
                "type": type(error).__name__,
                "details": details or str(error),
                "timestamp": datetime.now().isoformat(),
            },
            "status_code": status_code,
        }
    
    @staticmethod
    def format_success(
        data: Any,
        message: str = "Success",
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format successful response"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
        }


class ErrorHandler:
    """Centralized error handler for all endpoints"""
    
    logger = ProductionLogger("error_handler")
    
    # Error type mappings
    ERROR_TYPES = {
        "validation_error": {"status": 400, "message": "Validation error"},
        "not_found": {"status": 404, "message": "Resource not found"},
        "unauthorized": {"status": 401, "message": "Unauthorized"},
        "forbidden": {"status": 403, "message": "Forbidden"},
        "conflict": {"status": 409, "message": "Conflict"},
        "rate_limit": {"status": 429, "message": "Rate limit exceeded"},
        "internal_error": {"status": 500, "message": "Internal server error"},
    }
    
    @classmethod
    def handle_endpoint(cls, func: Callable) -> Callable:
        """Decorator to automatically handle errors in endpoints"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return ErrorResponse.format_success(
                    data=result,
                    message="Request successful"
                )
            except ValueError as e:
                cls.logger.warning(f"Validation error in {func.__name__}", error=e)
                return ErrorResponse.format_error(
                    e,
                    status_code=400,
                    message="Validation error"
                )
            except KeyError as e:
                cls.logger.warning(f"Missing required field in {func.__name__}", error=e)
                return ErrorResponse.format_error(
                    e,
                    status_code=400,
                    message="Missing required field"
                )
            except Exception as e:
                cls.logger.error(f"Unexpected error in {func.__name__}", error=e)
                return ErrorResponse.format_error(
                    e,
                    status_code=500,
                    message="An unexpected error occurred"
                )
        
        return wrapper
    
    @classmethod
    def wrap_async_function(cls, func: Callable, error_type: str = "internal_error") -> Callable:
        """Wrap async function with error handling"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_config = cls.ERROR_TYPES.get(error_type, cls.ERROR_TYPES["internal_error"])
                cls.logger.error(f"Error in {func.__name__}", error=e, error_type=error_type)
                raise Exception(f"{error_config['message']}: {str(e)}")
        
        return wrapper


# Global logger instance
logger = ProductionLogger("ceo_system")
