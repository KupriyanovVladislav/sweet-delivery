from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from uvicorn import run

from app.api.routes import api_router
from app.db import database


app = FastAPI()
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


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
    run('main:app', host='0.0.0.0', port=8000, reload=True)
