from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from backend.models import ProjectFolder

from .. import get_project_files
from .project_manuscript import ProjectManuscriptRouter
from .project_puzzledata import ProjectPuzzleDataRouter
from .project_settings import ProjectSettingsRouter
from .project_wordlist import ProjectWordlistRouter

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
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_folder: Annotated[ProjectFolder, Depends(get_project_files)],
) -> ProjectFolder:
    return project_folder


ProjectRouter.include_router(ProjectSettingsRouter)
ProjectRouter.include_router(ProjectWordlistRouter)
ProjectRouter.include_router(ProjectPuzzleDataRouter)
ProjectRouter.include_router(ProjectManuscriptRouter)
