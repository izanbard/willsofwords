from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from starlette.responses import FileResponse

from backend.models import PuzzleData
from backend.pages import Pages
from backend.utils import clear_marker_file, set_marker_file

from .. import (
    check_manuscript_exists,
    get_manuscript_path,
    load_puzzle_data,
)

ProjectManuscriptRouter = APIRouter(
    prefix="/manuscript",
    tags=["Project"],
)


@ProjectManuscriptRouter.post(
    "/",
    summary="Create a manuscript for a project in the background.",
    description="Create a manuscript for a project in the background.",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_manuscript(
    print_debug: bool,
    bg_tasks: BackgroundTasks,
    puzzle_data: Annotated[PuzzleData, Depends(load_puzzle_data)],
    manuscript_path: Annotated[FilePath, Depends(get_manuscript_path)],
) -> None:
    """Create a manuscript for a project in the background."""
    pages = Pages(
        word_search_data=puzzle_data,
        filename=manuscript_path,
        project_config=puzzle_data.project_config,
        print_debug=print_debug,
    )
    clear_marker_file(manuscript_path)
    set_marker_file(manuscript_path, 0)
    bg_tasks.add_task(pages.create_and_save_pages)
    return None


@ProjectManuscriptRouter.delete(
    "/",
    summary="Delete the manuscript for a project.",
    description="Delete the manuscript for a project.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_manuscript(manuscript_path: Annotated[FilePath, Depends(check_manuscript_exists)]) -> None:
    """Delete the manuscript for a project."""
    manuscript_path.unlink()
    return None


@ProjectManuscriptRouter.get(
    "/manuscript.pdf",
    summary="Get the manuscript pdf for a project.",
    description="Get the manuscript pdf for a project.",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
)
def get_manuscript(manuscript_path: Annotated[FilePath, Depends(check_manuscript_exists)]) -> FileResponse:
    """Get the manuscript pdf for a project."""
    return FileResponse(manuscript_path, media_type="application/pdf")
