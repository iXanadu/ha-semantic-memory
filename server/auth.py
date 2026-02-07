"""Optional bearer token authentication middleware.

If HAMEM_API_TOKEN is set, all requests (except /health) must include:
    Authorization: Bearer <token>

If HAMEM_API_TOKEN is empty (default), no authentication is required.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from server.config import settings

logger = logging.getLogger(__name__)


class BearerTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth if no token configured
        if not settings.api_token:
            return await call_next(request)

        # Always allow health checks without auth
        if request.url.path == "/health":
            return await call_next(request)

        # Check Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            client = request.client.host if request.client else "unknown"
            logger.warning(
                "AUTH FAILED: Missing Bearer token from %s on %s %s",
                client,
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Authentication required. Set Authorization: Bearer <token> header."
                },
            )

        token = auth_header[7:]  # Strip "Bearer "
        if token != settings.api_token:
            client = request.client.host if request.client else "unknown"
            logger.warning(
                "AUTH FAILED: Invalid token from %s on %s %s",
                client,
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API token."},
            )

        return await call_next(request)
