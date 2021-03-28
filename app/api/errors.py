from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse


async def validation_exception_handler(_: Request, exc: RequestValidationError):
    result = {'validation_error': [error for error in exc.errors()]}
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,  # 400 instead of 422
        content=jsonable_encoder(result),
    )
