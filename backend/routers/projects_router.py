from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from starlette.requests import Request

from backend.models import ProjectCreate, ProjectsList

from . import (
    check_project_path_exists,
    dir_copy,
    get_archive_project_path,
    get_data_path,
    get_project_path_from_name,
    get_project_settings_path,
    get_projects,
    load_project_settings,
)
from .project_routes.project_router import ProjectRouter

ProjectsRouter = APIRouter(
    prefix="/projects",
    tags=["Project"],
)


@ProjectsRouter.get(
    "/",
    response_model=ProjectsList,
    summary="Get the list of projects.",
    description="Returns a list of projects.",
    response_description="A list of projects.",
    status_code=status.HTTP_200_OK,
)
async def get_projects_route(projects_list: Annotated[ProjectsList, Depends(get_projects)]) -> ProjectsList:
    return projects_list


@ProjectsRouter.post(
    "/",
    response_model=ProjectsList,
    summary="Create a new project.",
    description="Creates a new project.",
    response_description="A list of projects.",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Project already exists"}},
)
async def create_project(project: ProjectCreate, req: Request):
    project_path = get_project_path_from_name(project.name, req)
    if project_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Project {project.name} already exists in {project_path}"
        )
    project_path.mkdir(parents=True)
    project.settings.save_config(get_project_settings_path(project_path, req))
    load_project_settings.cache_clear()
    return get_projects(get_data_path(req))


@ProjectsRouter.patch(
    "/{name}/{new_name}",
    summary="Rename or copy a project.",
    description="Rename or copy a project.",
    status_code=status.HTTP_200_OK,
    response_description="A list of projects.",
    response_model=ProjectsList,
    responses={404: {"description": "Project not found"}, 409: {"description": "Project already exists"}},
)
async def update_project(
    name: Annotated[str, Path(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")],
    new_name: Annotated[str, Path(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")],
    req: Request,
    copy: bool = False,
):
    old_path = get_project_path_from_name(name, req)
    new_path = get_project_path_from_name(new_name, req)
    if not old_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    if new_path.exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Project {new_name} already exists")
    if copy:
        new_path.mkdir(parents=True)
        dir_copy(old_path, new_path)
    else:
        old_path.rename(new_path)
    return get_projects(get_data_path(req))


@ProjectsRouter.delete(
    "/{name}",
    summary="Archive a project.",
    description="Archive a project.",
    status_code=status.HTTP_200_OK,
    response_description="A list of projects.",
    response_model=ProjectsList,
    responses={404: {"description": "Project not found"}},
)
async def archive_project(
    req: Request,
    project_path: Annotated[FilePath, Depends(check_project_path_exists)],
    archive_path: Annotated[FilePath, Depends(get_archive_project_path)],
):
    project_path.rename(archive_path)
    return get_projects(get_data_path(req))


ProjectsRouter.include_router(ProjectRouter)
