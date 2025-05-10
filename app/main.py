from config.initializers import initialize_all

# initialize_all()

from fastapi import FastAPI
from app.api.v0 import router as v0Router
from app.api.exception_handlers import register_exception_handlers


def create_app():
    app = FastAPI(title="Perfi")
    app.include_router(router=v0Router)
    register_exception_handlers(app)

    return app


if __name__ == "__main__":
    initialize_all()
    app = create_app()
else:
    app = create_app()
