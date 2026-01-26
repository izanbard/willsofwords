from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from starlette import status

from backend.models import (
    ProjectConfig,
    Puzzle,
    PuzzleBaseData,
    PuzzleData,
    PuzzleLetter,
    Wordlist,
)
from backend.utils import clear_marker_file, set_marker_file

from .. import (
    check_puzzle_data_exists,
    get_puzzle_data_path,
    load_project_settings,
    load_puzzle_data,
    validate_word_lists,
)

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
    bg_tasks: BackgroundTasks,
    wordlist: Annotated[Wordlist, Depends(validate_word_lists)],
    puzzle_config: Annotated[ProjectConfig, Depends(load_project_settings)],
    puzzle_data_path: FilePath = Depends(get_puzzle_data_path),
) -> None:
    """Create puzzle data for a project in the background."""
    wordsearch = PuzzleData(project_config=puzzle_config, book_title=wordlist.title, wordlist=wordlist)
    clear_marker_file(puzzle_data_path)
    set_marker_file(puzzle_data_path, 0)
    load_puzzle_data.cache_clear()
    bg_tasks.add_task(wordsearch.create_and_save_data, puzzle_data_path)

    return None


@ProjectPuzzleDataRouter.delete(
    "/",
    summary="Delete puzzle data for a project.",
    description="Delete puzzle data for a project.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_puzzledata(puzzledata_path: Annotated[FilePath, Depends(check_puzzle_data_exists)]) -> None:
    puzzledata_path.unlink()
    load_puzzle_data.cache_clear()
    return None


@ProjectPuzzleDataRouter.get(
    "/base_data/",
    summary="Get base puzzle data for a project.",
    description="Get base puzzle data for a project.",
    status_code=status.HTTP_200_OK,
    response_model=PuzzleBaseData,
    response_description="The base puzzle data for the project.",
)
def get_base_puzzledata(puzzle_data: Annotated[PuzzleData, Depends(load_puzzle_data)]) -> PuzzleBaseData:
    return PuzzleBaseData(
        title=puzzle_data.book_title, puzzle_list=puzzle_data.get_puzzle_ids(), page_count=puzzle_data.page_count
    )


@ProjectPuzzleDataRouter.get(
    "/puzzle/{puzzle_id}/",
    summary="Get puzzle data for a puzzle.",
    description="Get puzzle data for a puzzle.",
    status_code=status.HTTP_200_OK,
    response_model=Puzzle,
    response_description="The puzzle data for the puzzle.",
)
def get_puzzle_data(puzzle_id: str, puzzle_data: Annotated[PuzzleData, Depends(load_puzzle_data)]) -> Puzzle:
    try:
        puzzle = puzzle_data.get_puzzle_by_id(puzzle_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found")
    return puzzle


@ProjectPuzzleDataRouter.put(
    "/puzzle/{puzzle_id}/",
    summary="change the puzzledata for this puzzle",
    description="Change the title of a puzzle.",
    status_code=status.HTTP_200_OK,
)
def update_puzzle(
    puzzle_id: str,
    new_puzzle: Puzzle,
    puzzle_data_path: Annotated[FilePath, Depends(get_puzzle_data_path)],
    puzzle_data: Annotated[PuzzleData, Depends(load_puzzle_data)],
) -> Puzzle:
    try:
        puzzle_data.update_puzzle_by_id(puzzle_id, new_puzzle)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found ")
    puzzle_data.save_data(puzzle_data_path)
    load_puzzle_data.cache_clear()
    return new_puzzle


@ProjectPuzzleDataRouter.delete(
    "/puzzle/{puzzle_id}/",
    summary="Delete a puzzle and rebuild it",
    description="Delete a puzzle and rebuild it",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_puzzle(
    puzzle_id: str,
    puzzle_data_path: Annotated[FilePath, Depends(get_puzzle_data_path)],
    puzzle_data: Annotated[PuzzleData, Depends(load_puzzle_data)],
) -> None:
    try:
        puzzle = puzzle_data.get_puzzle_by_id(puzzle_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found")
    puzzle.puzzle_reset()
    puzzle.populate_puzzle()
    puzzle.check_for_inadvertent_profanity()
    puzzle_data.save_data(puzzle_data_path)
    load_puzzle_data.cache_clear()
    return None


@ProjectPuzzleDataRouter.put(
    "/puzzle/{puzzle_id}/cell/{x}/{y}/",
    summary="Change the letter in a puzzle cell.",
    description="Change the letter in a puzzle cell.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_letter_in_puzzle(
    puzzle_id: str,
    x: int,
    y: int,
    new_letter: PuzzleLetter,
    puzzle_data_path: Annotated[FilePath, Depends(get_puzzle_data_path)],
    puzzle_data: Annotated[PuzzleData, Depends(load_puzzle_data)],
) -> None:
    try:
        puzzle = puzzle_data.get_puzzle_by_id(puzzle_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Puzzle {puzzle_id} not found")
    puzzle.cells[y][x].value = new_letter.letter
    puzzle.check_for_inadvertent_profanity()
    puzzle_data.save_data(puzzle_data_path)
    load_puzzle_data.cache_clear()
    return None
