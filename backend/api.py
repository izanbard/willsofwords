import sys
from contextlib import asynccontextmanager
from io import StringIO
from typing import AsyncIterator

from fastapi import FastAPI, Response, Request, status
from fastapi.responses import JSONResponse
from yaml import dump as yaml_dump

from backend.routers import ProjectRouter
from backend.utils import Logger, create_env_file_if_not_exists, get_config, Config
from backend.pages import PrintParams

from .commands import execute_command
from .routers.settings_router import SettingsRouter


def fix_puzzle_config(config: Config):
    if config.puzzle.max_columns == 0:
        print_params = PrintParams()
        config.puzzle.calculate_column_count(print_params.grid_width, print_params.min_cell_size)
    if config.puzzle.max_rows == 0:
        print_params = PrintParams()
        config.puzzle.calculate_max_row_count(print_params.grid_height_two_page, print_params.min_cell_size)
    if config.puzzle.medium_rows == 0:
        print_params = PrintParams()
        config.puzzle.calculate_medium_row_count(print_params.grid_height, print_params.min_cell_size)


def initialise():
    create_env_file_if_not_exists()
    config = get_config()
    fix_puzzle_config(config)
    Logger(config.app)
    return config


@asynccontextmanager
async def app_lifespan_startup_and_shutdown(app: FastAPI) -> AsyncIterator[None]:
    # before app is created
    config = initialise()
    if config.app.command != "api":
        sys.exit(execute_command(config.app, config.puzzle, config.print, command=config.app.command))
    app.state.config = config
    with open("version.txt") as f:
        app.state.version = f.readline().strip()
    # yield to the app
    yield
    # after the app shuts down


def create_api() -> FastAPI:
    logger = Logger.get_logger()
    with open("version.txt") as f:
        version = f.readline().strip()
    tags_metadata = [
        {"name": "Project", "description": "Endpoint Collection for Wordsworth Puzzles"},
        {"name": "Command", "description": "Endpoint Collection for Puzzles"},
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

    api.include_router(ProjectRouter)
    api.include_router(SettingsRouter)

    @api.get(
        "/openapi.yaml",
        status_code=200,
        response_class=Response,
        include_in_schema=False,
    )
    async def yaml_spec() -> Response:
        spec_str = StringIO()
        yaml_dump(api.openapi(), spec_str, sort_keys=False)
        return Response(spec_str.getvalue(), media_type="text/yaml")

    api.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, internal_exception_handler)
    logger.info("API created")
    return api


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
