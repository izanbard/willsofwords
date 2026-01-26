import json
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import Depends, HTTPException, Path
from starlette import status
from starlette.requests import Request

# from .projects_router import ProjectsRouter  # noqa: F401
from ..models import (
    ProfanityList,
    ProjectConfig,
    ProjectFile,
    ProjectFolder,
    PuzzleData,
    Wordlist,
)
from ..utils import get_profanity_list


def sanitise_user_input_path(path: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", path)


def get_project_path_from_name(
    name: Annotated[str, Path(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")], req: Request
) -> FilePath:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder)
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    project_dir = data_dir / name
    if not str(project_dir.resolve()).startswith(str(data_dir.resolve())):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access other parts of the file system"
        )
    return project_dir


def get_project_settings_path(project_dir: Annotated[FilePath, Depends(get_project_path_from_name)], req: Request) -> FilePath:
    return project_dir / req.state.config.app.project_settings


def check_project_settings_exists(project_settings_path: Annotated[FilePath, Depends(get_project_settings_path)]) -> FilePath:
    if not project_settings_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project settings not found")
    return project_settings_path


@lru_cache(maxsize=5)
def load_project_settings(project_settings_path: Annotated[FilePath, Depends(check_project_settings_exists)]) -> ProjectConfig:
    with open(project_settings_path, "r") as fd:
        project_settings = ProjectConfig(**json.load(fd))
    return project_settings


def get_wordlist_path(project_dir: Annotated[FilePath, Depends(get_project_path_from_name)], req: Request) -> FilePath:
    return project_dir / req.state.config.app.input_filename


def check_wordlist_exists(wordlist_path: Annotated[FilePath, Depends(get_wordlist_path)]) -> FilePath:
    if not wordlist_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wordlist not found")
    return wordlist_path


@lru_cache(maxsize=5)
def load_wordlist(wordlist_path: Annotated[FilePath, Depends(check_wordlist_exists)]) -> Wordlist:
    with open(wordlist_path, "r") as fd:
        wordlist = Wordlist(**json.load(fd))
    return wordlist


def validate_word_lists(wordlist: Annotated[Wordlist, Depends(load_wordlist)]) -> Wordlist:
    validation_dict = wordlist.validate_word_lists()
    if validation_dict["profanity"] or validation_dict["illegal_chars"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wordlist contains invalid words. Profanity: {validation_dict['profanity']}, Illegal Chars: {validation_dict['illegal_chars']}",
        )
    return wordlist


def get_puzzle_data_path(
    project_dir: Annotated[FilePath, Depends(get_project_path_from_name)],
    req: Request,
) -> FilePath:
    puzzle_data_path = project_dir / req.state.config.app.data_filename
    return puzzle_data_path


def check_puzzle_data_exists(puzzle_data_path: Annotated[FilePath, Depends(get_puzzle_data_path)]) -> FilePath:
    if not puzzle_data_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Puzzle data not found")
    return puzzle_data_path


@lru_cache(maxsize=5)
def load_puzzle_data(
    puzzle_data_path: Annotated[FilePath, Depends(check_puzzle_data_exists)],
) -> PuzzleData:
    with open(puzzle_data_path, "r") as fd:
        puzzle_data = PuzzleData(**json.load(fd))
    return puzzle_data


def get_manuscript_path(project_dir: Annotated[FilePath, Depends(get_project_path_from_name)], req: Request) -> FilePath:
    return project_dir / req.state.config.app.output_filename


def check_manuscript_exists(manuscript_path: Annotated[FilePath, Depends(get_manuscript_path)]) -> FilePath:
    if not manuscript_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscript not found")
    return manuscript_path


def get_project_files(project_dir: Annotated[FilePath, Depends(get_project_path_from_name)]) -> ProjectFolder:
    project_files = [
        ProjectFile(name=file.name, modified_date=datetime.fromtimestamp(file.stat().st_mtime))
        for file in project_dir.iterdir()
        if file.is_file()
    ]
    project_files.sort(key=lambda x: x.name.lower())
    project_folder = ProjectFolder(name=project_dir.name, project_files=project_files)
    return project_folder


def get_profanity_list_model() -> ProfanityList:
    return ProfanityList(word_list=get_profanity_list())
