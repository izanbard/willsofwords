from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request

from .project_routes.project_router import ProjectRouter
from backend.models import ProjectConfig, ProjectFolder, ProjectFile, ProjectsList, ProjectCreate
from backend.utils import get_project_settings_defaults, save_project_settings

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
    data_dir = Path(req.state.config.app.data_folder)
    projects_list = []
    for project in [project for project in data_dir.iterdir() if project.is_dir()]:
        project_files = [
            ProjectFile(name=file.name, modified_date=datetime.fromtimestamp(file.stat().st_mtime))
            for file in project.iterdir()
            if file.is_file()
        ]
        project_folder = ProjectFolder(name=project.name, project_files=project_files)
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
    data_dir = Path(req.state.config.app.data_folder)
    if project.name in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Project {project.name} already exists")
    default_config = ProjectConfig(**get_project_settings_defaults())
    updates = project.settings.model_dump(exclude_unset=True)
    project_config = default_config.model_copy(update=updates)
    project_dir = data_dir / project.name
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
async def update_project(name: str, new_name: str, req: Request, copy: bool = False):
    data_dir = Path(req.state.config.app.data_folder)
    if name not in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    if new_name in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Project {new_name} already exists")

    def dir_copy(src: Path, dst: Path):
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
async def archive_project(name: str, req: Request):
    data_dir = Path(req.state.config.app.data_folder)
    if name not in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    archives_dir = Path(req.state.config.app.archive_folder)
    if name in [proj.stem for proj in archives_dir.iterdir()]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project {name} already archived, please manually delete old project from archive and try again",
        )
    (data_dir / name).rename(archives_dir / name)
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
async def restore_project(name: str, req: Request):
    data_dir = Path(req.state.config.app.data_folder)
    if name in [proj.stem for proj in data_dir.iterdir()]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project {name} already exists, please manually rename archive and try again",
        )
    archives_dir = Path(req.state.config.app.archive_folder)
    if name not in [proj.stem for proj in archives_dir.iterdir()]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} does not exist")
    (archives_dir / name).rename(data_dir / name)
    return await get_projects(req)


ProjectsRouter.include_router(ProjectRouter)
