from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from backend.models import ProjectConfig
from backend.routers import get_project_settings_path, load_project_settings, get_data_path, check_file_path_in_data_path

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
async def get_settings(project_config: Annotated[ProjectConfig, Depends(load_project_settings)]) -> ProjectConfig:
    return project_config


@ProjectSettingsRouter.put(
    "/",
    summary="Update the named project settings",
    description="Updates the project settings",
    status_code=status.HTTP_200_OK,
    response_description="The updated project settings.",
    response_model=ProjectConfig,
)
async def update_settings(
    new_settings: ProjectConfig, project_settings_path: Annotated[FilePath, Depends(get_project_settings_path)], req: Request
) -> ProjectConfig:
    if check_file_path_in_data_path(project_settings_path, get_data_path(req)):
        new_settings.save_config(project_settings_path)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access other parts of the file system"
        )
    return new_settings
