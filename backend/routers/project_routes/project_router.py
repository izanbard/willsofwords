from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from .command_router import CommandRouter
from backend.models import ProjectFolder
from . import get_project_files

ProjectRouter = APIRouter(
    prefix="/project/{name}",
    tags=["Project"],
)


@ProjectRouter.get(
    "/",
    response_model=ProjectFolder,
    summary="Get the named project ",
    description="Returns the project folder contents",
    response_description="The project folder.",
    status_code=200,
)
async def get_project(name: str, req: Request) -> ProjectFolder:
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project {name} not found")
    project_folder = get_project_files(data_dir)
    return project_folder


ProjectRouter.include_router(CommandRouter)
