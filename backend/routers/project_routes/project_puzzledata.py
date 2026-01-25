import json
from functools import lru_cache
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, HTTPException, BackgroundTasks, Path
from starlette import status
from starlette.requests import Request

from backend.models import Wordlist, PuzzleData, ProjectConfig, PuzzleBaseData, Puzzle, PuzzleLetter
from backend.utils import clear_marker_file, set_marker_file, sanitise_user_input_path

ProjectPuzzleDataRouter = APIRouter(
    prefix="/puzzledata",
    tags=["Project"],
)


@ProjectPuzzleDataRouter.post(
    "/",
    summary="Create puzzle data for a project in the background.",
    description="Create puzzle data for a project in the background.",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_puzzledata(
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request, bg_tasks: BackgroundTasks
) -> None:
    """Create puzzle data for a project in the background."""
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    input_file = data_dir / req.state.config.app.input_filename
    with open(input_file) as fd:
        wordlist = Wordlist(**json.load(fd))
    validation_dict = wordlist.validate_word_lists()
    if validation_dict["profanity"] or validation_dict["illegal_chars"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wordlist contains invalid words. Profanity: {validation_dict['profanity']}, Illegal Chars: {validation_dict['illegal_chars']}",
        )
    with open(data_dir / req.state.config.app.project_settings, "r") as f:
        puzzle_config = ProjectConfig(**json.load(f))

    wordsearch = PuzzleData(project_config=puzzle_config, book_title=wordlist.title, wordlist=wordlist)
    data_file = data_dir / req.state.config.app.data_filename
    clear_marker_file(data_file)
    set_marker_file(data_file, 0)
    load_the_puzzle_data.cache_clear()
    bg_tasks.add_task(wordsearch.create_and_save_data, data_file)

    return None


@ProjectPuzzleDataRouter.delete(
    "/",
    summary="Delete puzzle data for a project.",
    description="Delete puzzle data for a project.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_puzzledata(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request) -> None:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzledata_path = data_dir / req.state.config.app.data_filename
    if puzzledata_path.exists():
        puzzledata_path.unlink()
    load_the_puzzle_data.cache_clear()
    return None


@ProjectPuzzleDataRouter.get(
    "/base_data/",
    summary="Get base puzzle data for a project.",
    description="Get base puzzle data for a project.",
    status_code=status.HTTP_200_OK,
    response_model=PuzzleBaseData,
    response_description="The base puzzle data for the project.",
)
def get_base_puzzledata(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request) -> PuzzleBaseData:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzle_data = load_the_puzzle_data(data_dir / req.state.config.app.data_filename)
    return PuzzleBaseData(
        title=puzzle_data.book_title, puzzle_list=puzzle_data.get_puzzle_ids(), page_count=puzzle_data.page_count
    )


@lru_cache
def load_the_puzzle_data(filename: FilePath) -> PuzzleData:
    with open(filename, "r") as f:
        puzzle_data = PuzzleData(**json.load(f))
    return puzzle_data


@ProjectPuzzleDataRouter.get(
    "/puzzle/{puzzle_id}/",
    summary="Get puzzle data for a puzzle.",
    description="Get puzzle data for a puzzle.",
    status_code=status.HTTP_200_OK,
    response_model=Puzzle,
    response_description="The puzzle data for the puzzle.",
)
def get_puzzle_data(
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], puzzle_id: str, req: Request
) -> Puzzle:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzle_data = load_the_puzzle_data(data_dir / req.state.config.app.data_filename)
    if puzzle_id not in puzzle_data.get_puzzle_ids():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found in project {name}")
    return puzzle_data.get_puzzle_by_id(puzzle_id)


@ProjectPuzzleDataRouter.put(
    "/puzzle/{puzzle_id}/",
    summary="change the puzzledata for this puzzle",
    description="Change the title of a puzzle.",
    status_code=status.HTTP_200_OK,
)
def update_puzzle(
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], puzzle_id: str, new_puzzle: Puzzle, req: Request
) -> Puzzle:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzle_data = load_the_puzzle_data(data_dir / req.state.config.app.data_filename)
    try:
        puzzle_data.update_puzzle_by_id(puzzle_id, new_puzzle)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found in project {name}")
    puzzle_data.save_data(data_dir / req.state.config.app.data_filename)
    return new_puzzle


@ProjectPuzzleDataRouter.delete(
    "/puzzle/{puzzle_id}/",
    summary="Delete a puzzle and rebuild it",
    description="Delete a puzzle and rebuild it",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_puzzle(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], puzzle_id: str, req: Request) -> None:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzle_data = load_the_puzzle_data(data_dir / req.state.config.app.data_filename)
    try:
        puzzle = puzzle_data.get_puzzle_by_id(puzzle_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found in project {name}")
    puzzle.puzzle_reset()
    puzzle.populate_puzzle()
    puzzle.check_for_inadvertent_profanity()
    puzzle_data.save_data(data_dir / req.state.config.app.data_filename)
    return None


@ProjectPuzzleDataRouter.put(
    "/puzzle/{puzzle_id}/cell/{x}/{y}/",
    summary="Change the letter in a puzzle cell.",
    description="Change the letter in a puzzle cell.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_letter_in_puzzle(
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")],
    puzzle_id: str,
    x: int,
    y: int,
    new_letter: PuzzleLetter,
    req: Request,
) -> None:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    puzzle_data = load_the_puzzle_data(data_dir / req.state.config.app.data_filename)
    puzzle = puzzle_data.get_puzzle_by_id(puzzle_id)
    if puzzle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found in project {name}")
    puzzle.cells[y][x].value = new_letter.letter
    puzzle.check_for_inadvertent_profanity()
    puzzle_data.save_data(data_dir / req.state.config.app.data_filename)
    return None
