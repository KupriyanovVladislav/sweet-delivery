from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from uvicorn import run

from app.api.errors import validation_exception_handler
from app.api.routes import api_router
from app.db import database


async def startup():
    await database.connect()


async def shutdown():
    await database.disconnect()


def get_application() -> FastAPI:
    application = FastAPI(
        title="Sweet delivery",
        description=(
            "Training project for Yandex academy."
            + "\nWARNING! 400 (bad request) will be instead of 422 (validation error)."
            + "\nIf you see 422 in the documentation, ignore it. Keep in mind the note above"
            + "\nBody of 400 response may differ!"
        ),
    )

    application.add_event_handler("startup", startup)
    application.add_event_handler("shutdown", shutdown)

    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    application.include_router(api_router)
    return application


app = get_application()


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080)
