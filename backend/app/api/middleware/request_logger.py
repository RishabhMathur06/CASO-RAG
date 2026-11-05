# Imports dependencies.
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger

class RequestAuditMiddleware(BaseHTTPMiddleware):
    """
        Production HTTP Middleware:
            1. Measures end-to-end request duration and attaches an 'X-Process-Time-Ms' header.
            2. Logs structured audit entries (Method, Path, Status Code, Duration).
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        # Process the incoming request through downstream routers.
        response = await call_next(request)

        # Calculate total latency in milliseconds.
        process_time_ms = (time.perf_counter() - start_time) * 1000

        # Attach process time header to HTTP response.
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
        client_host = request.client.host if request.client else "unknown"

        logger.info(
            f"HTTP {request.method} {request.url.path} -> Status: {response.status_code} "
            f"| Time: {process_time_ms:.2f}ms | Client: {client_host}"
        )

        return response