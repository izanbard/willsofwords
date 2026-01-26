from contextlib import asynccontextmanager
from io import StringIO
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_bgtasks_dashboard import mount_bg_tasks_dashboard
from starlette.responses import RedirectResponse
from yaml import dump as yaml_dump

from backend.utils import Config, Logger

from .routers.projects_router import ProjectsRouter
from .routers.settings_router import SettingsRouter


@asynccontextmanager
async def app_lifespan_startup_and_shutdown(app: FastAPI) -> AsyncIterator[dict]:
    # before the app is created
    app.state.version = app.version
    config = Config()
    logger = Logger(config.app).get_logger()
    # yield to the app
    yield {"config": config, "logger": logger}
    # after the app shuts down
    logger.info("Application shutdown complete")


def inject_coors_settings(api: FastAPI):
    api.add_middleware(
        CORSMiddleware,
        allow_origins=[Config().app.frontend_host_for_cors],
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
            "HEAD",
            "PATCH",
            "TRACE",
            "CONNECT",
        ],
        allow_headers=[
            "Accept",
            "Accept-Encoding",
            "Accept-Language",
            "Connection",
            "Host",
            "Keep-Alive",
            "Origin",
            "Referer",
            "Sec-Fetch-Dest",
            "Sec-Fetch-Mode",
            "Sec-Fetch-Site",
            "User-Agent",
            "sec-ch-ua",
            "sec-ch-ua-mobile",
            "sec-ch-ua-platform",
            "sec-gpc",
        ],
    )


def internal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    content = {
        "code": 500,
        "msg": "Internal Server Error",
        "type": type(exc).__name__,
        "detail": str(exc),
    }
    Logger.get_logger().error(
        f"Returning 500 due to exception: {type(exc).__name__}, {str(exc)}, for {request.method} to {request.url}"
    )
    return JSONResponse(
        status_code=500,
        content=content,
    )


def create_api() -> FastAPI:
    logger = Logger.get_logger()
    with open("version.txt") as f:
        version = f.readline().strip()
    tags_metadata = [
        {"name": "Project", "description": "Endpoint Collection for Wordsworth Puzzles"},
        {"name": "Settings", "description": "Endpoint Collection for Settings"},
    ]
    logger.info(f"Creating the API... version: {version}")
    api = FastAPI(
        title="Wordsworth Puzzles API",
        openapi_url="/openapi.json",
        version=version,
        openapi_tags=tags_metadata,
        external_docs={"description": "Yaml API Spec", "url": "/openapi.yaml"},
        lifespan=app_lifespan_startup_and_shutdown,
    )

    inject_coors_settings(api)
    mount_bg_tasks_dashboard(api)

    @api.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["Connection"] = "keep-alive"
        response.headers["Keep-Alive"] = "timeout=120, max=100"
        return response

    api.include_router(ProjectsRouter)
    api.include_router(SettingsRouter)
    api.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, internal_exception_handler)

    @api.get(
        "/openapi.yaml",
        status_code=200,
        response_class=Response,
        include_in_schema=False,
        description="YAML API specification",
    )
    async def yaml_spec() -> Response:
        spec_str = StringIO()
        yaml_dump(api.openapi(), spec_str, sort_keys=False)
        return Response(spec_str.getvalue(), media_type="text/yaml")

    @api.get(
        "/", status_code=302, include_in_schema=False, response_class=RedirectResponse, description="Redirect to the API docs"
    )
    async def root() -> RedirectResponse:
        return RedirectResponse("/docs")

    logger.info("API created")
    return api
