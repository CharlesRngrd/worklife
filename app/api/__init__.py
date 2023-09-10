from fastapi import FastAPI

from .routes import employee, health, vacation


def add_app_routes(app: FastAPI) -> None:
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(employee.router, prefix="/employee", tags=["Employee"])
    app.include_router(vacation.router, prefix="/vacation", tags=["Vacation"])
