import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request, status, HTTPException
from starlette.responses import FileResponse

from backend.models import PuzzleData
from backend.pages import Pages
from backend.utils import clear_marker_file, set_marker_file

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
    name: str,
    print_debug: bool,
    req: Request,
    bg_tasks: BackgroundTasks,
) -> None:
    """Create a manuscript for a project in the background."""
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzle_data_path = data_dir / req.state.config.app.data_filename
    if not puzzle_data_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} puzzle data not found")
    with open(puzzle_data_path, "r") as fd:
        puzzle_data = PuzzleData(**json.load(fd))

    manuscript_path = data_dir / req.state.config.app.output_filename
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
def delete_manuscript(name: str, req: Request) -> None:
    """Delete the manuscript for a project."""
    data_dir = Path(req.state.config.app.data_folder) / name
    manuscript_path = data_dir / req.state.config.app.output_filename
    if manuscript_path.exists():
        manuscript_path.unlink()
    return None


@ProjectManuscriptRouter.get(
    "/manuscript.pdf",
    summary="Get the manuscript pdf for a project.",
    description="Get the manuscript pdf for a project.",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
)
def get_manuscript(name: str, req: Request) -> FileResponse:
    """Get the manuscript pdf for a project."""
    data_dir = Path(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    manuscript_path = data_dir / req.state.config.app.output_filename
    if not manuscript_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Manuscript for project {name} not found")
    return FileResponse(manuscript_path, media_type="application/pdf")
