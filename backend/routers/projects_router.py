import uuid
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from starlette import status
from starlette.requests import Request

from .project_routes.project_router import ProjectRouter
from backend.models import ProjectConfig, ProjectsList, ProjectCreate
from backend.utils import get_project_settings_defaults, save_project_settings, sanitise_user_input_path
from .project_routes import get_project_files

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
async def get_projects(req: Request) -> ProjectsList:
    data_dir = FilePath(req.state.config.app.data_folder)
    projects_list = []
    for project in [project for project in data_dir.iterdir() if project.is_dir()]:
        project_folder = get_project_files(project)
        projects_list.append(project_folder)
    projects_list.sort(key=lambda x: x.name.lower())
    return ProjectsList(projects=projects_list)


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
    data_dir = FilePath(req.state.config.app.data_folder)
    project_name = sanitise_user_input_path(project.name)
    if project_name in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Project {project.name} already exists")
    default_config = ProjectConfig(**get_project_settings_defaults())
    updates = project.settings.model_dump(exclude_unset=True)
    project_config = default_config.model_copy(update=updates)
    project_dir = data_dir / project_name
    project_dir.mkdir(parents=True)
    save_project_settings(project_config.model_dump(), project_dir / req.state.config.app.project_settings)
    return await get_projects(req)


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
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")],
    new_name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")],
    req: Request,
    copy: bool = False,
):
    name = sanitise_user_input_path(name)
    new_name = sanitise_user_input_path(new_name)
    data_dir = FilePath(req.state.config.app.data_folder)
    if name not in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    if new_name in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Project {new_name} already exists")

    def dir_copy(src: FilePath, dst: FilePath):
        for root, dirs, files in src.walk():
            for file in files:
                with open(root / file, "rb") as fd:
                    with open(dst / file, "wb") as tfd:
                        tfd.write(fd.read())
            for directory in dirs:
                (dst / directory).mkdir(parents=True)
                dir_copy(root / directory, dst / directory)

    if copy:
        (data_dir / new_name).mkdir(parents=True)
        dir_copy(data_dir / name, data_dir / new_name)
    else:
        (data_dir / name).rename(data_dir / new_name)
    return await get_projects(req)


@ProjectsRouter.delete(
    "/{name}",
    summary="Archive a project.",
    description="Archive a project.",
    status_code=status.HTTP_200_OK,
    response_description="A list of projects.",
    response_model=ProjectsList,
    responses={404: {"description": "Project not found"}},
)
async def archive_project(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request):
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder)
    if name not in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    archives_dir = FilePath(req.state.config.app.archive_folder)
    new_name = f"{name}_{uuid.uuid4().hex[:8]}"
    if new_name in [proj.stem for proj in archives_dir.iterdir()]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project {new_name} already archived, please manually delete old project from archive and try again",
        )
    (data_dir / name).rename(archives_dir / new_name)
    return await get_projects(req)


@ProjectsRouter.put(
    "/{name}",
    summary="Restore a project.",
    description="Restore a project.",
    status_code=status.HTTP_200_OK,
    response_description="A list of projects.",
    response_model=ProjectsList,
    responses={404: {"description": "Project not found"}},
)
async def restore_project(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request):
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder)
    if name in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project {name} already exists, please manually rename archive and try again",
        )
    archives_dir = FilePath(req.state.config.app.archive_folder)
    if name not in [proj.stem for proj in archives_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    (archives_dir / name).rename(data_dir / name)
    return await get_projects(req)


ProjectsRouter.include_router(ProjectRouter)
