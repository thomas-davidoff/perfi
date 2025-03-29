from fastapi.responses import JSONResponse
from perfi.core.exc import CustomException
from fastapi import Request
import time
import secrets
import logging

logger = logging.getLogger(__name__)


async def log_request(request: Request, call_next):
    """
    Middleware to log incoming requests with a semi-unique request ID.
    Logs client info, HTTP scheme, response status code, and processing time.
    """
    request_id = secrets.token_hex(4)
    client = f"{request.client.host}:{request.client.port} with request id {request_id}"

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = round(time.perf_counter() - start_time, 3)
    response.headers["X-Process-Time"] = str(process_time)

    status_code = response.status_code

    msg = (
        f"Completed {request.url} with {status_code} for {client} "
        f"in {process_time} seconds"
    )

    if status_code < 400:
        logger.info(msg)
    else:
        logger.warning(msg)

    return response
