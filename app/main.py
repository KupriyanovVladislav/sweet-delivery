from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from uvicorn import run

from app.api.routes import api_router
from app.db import database

app = FastAPI()
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    result = {'validation_error': [error for error in exc.errors()]}
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(result),
    )


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root(param: int):
    return {"message": param}


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080)
