from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from .routers import email, ticket, image, status
from .config import get_settings


def create_app():
    settings = get_settings()
    app = FastAPI(debug=True)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError,
                              request_validation_exception_handler)

    for router in [email, ticket, image, status]:
        router.config(app, settings)
    return app
