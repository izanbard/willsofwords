import json
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from starlette import status
from starlette.requests import Request


from backend.models import ProjectConfigUpdate, ProjectConfig
from backend.utils import get_project_settings_defaults, save_project_settings

ProjectSettingsRouter = APIRouter(
    prefix="/settings",
    tags=["Project"],
)


@ProjectSettingsRouter.get(
    "/",
    response_model=ProjectConfig,
    summary="Get the named project settings",
    description="Returns the project settings",
    response_description="The project settings.",
    status_code=status.HTTP_200_OK,
)
async def get_settings(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request) -> ProjectConfig:
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} settings not found")
    if (data_dir / req.state.config.app.project_settings).exists():
        with open(data_dir / req.state.config.app.project_settings, "r") as f:
            return ProjectConfig(**json.load(f))
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} settings not found")


@ProjectSettingsRouter.put(
    "/",
    summary="Update the named project settings",
    description="Updates the project settings",
    status_code=status.HTTP_200_OK,
    response_description="The updated project settings.",
    response_model=ProjectConfig,
)
async def update_settings(
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request, settings: ProjectConfigUpdate
) -> ProjectConfig:
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    default_config = ProjectConfig(**get_project_settings_defaults())
    updates = settings.model_dump(exclude_unset=True)
    new_config = default_config.model_copy(update=updates)
    save_project_settings(new_config.model_dump(), data_dir / req.state.config.app.project_settings)
    return new_config
