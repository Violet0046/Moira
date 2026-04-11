from fastapi import FastAPI

from moira.api.router import api_router
from moira.core.config import settings
from moira.core.logging import configure_logging


configure_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
