from fastapi import FastAPI

from .routers import email, ticket, image
from .config import get_settings


def create_app():
    settings = get_settings()
    app = FastAPI()

    for router in [email, ticket, image]:
        router.config(app, settings)
    return app
