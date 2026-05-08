"""
Logging middleware for FastAPI
"""
import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        logger.info(f"Request: {method} {path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Response: {method} {path} - Status {response.status_code} - {process_time:.3f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error: {method} {path} - {str(e)} - {process_time:.3f}s")
            raise
