import json
import re
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request, status, WebSocket
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from ..models import (
    ProfanityList,
    ProjectConfig,
    ProjectFile,
    ProjectFolder,
    ProjectsList,
    PuzzleData,
    Wordlist,
    PuzzleInput,
)
from ..models.wordlist import WordlistInput
from ..utils import get_profanity_list


def sanitise_user_input_path(path: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", path)


def get_data_path(req: Request) -> FilePath:
    return FilePath(req.state.config.app.data_folder)


def get_archive_path(req: Request) -> FilePath:
    return FilePath(req.state.config.app.archive_folder)


def check_file_path_in_data_path(target_path: FilePath, data_path: FilePath) -> FilePath:
    if str(target_path.resolve()).startswith(str(data_path.resolve())):
        return target_path
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access other parts of the file system")


def get_project_path_from_name(
    name: Annotated[str, Path(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")], req: Request
) -> FilePath:
    name = sanitise_user_input_path(name)
    data_dir = get_data_path(req)
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    project_dir = data_dir / name
    project_dir_safe = check_file_path_in_data_path(project_dir, data_dir)
    return project_dir_safe


def check_project_path_exists(project_dir: Annotated[FilePath, Depends(get_project_path_from_name)]) -> FilePath:
    if not project_dir.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
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


def get_archive_project_path(
    name: Annotated[str, Path(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")],
    req: Request,
) -> FilePath:
    new_name_path = get_archive_path(req) / f"{name}_{uuid.uuid4().hex[:8]}"
    if new_name_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project {name}  archive conflict, please manually delete old project from archive and try again",
        )
    return new_name_path


def get_project_files(project_dir: Annotated[FilePath, Depends(get_project_path_from_name)]) -> ProjectFolder:
    project_files = [
        ProjectFile(name=file.name, modified_date=datetime.fromtimestamp(file.stat().st_mtime))
        for file in project_dir.iterdir()
        if file.is_file()
    ]
    project_files.sort(key=lambda x: x.name.lower())
    project_folder = ProjectFolder(name=project_dir.name, project_files=project_files)
    return project_folder


def get_projects(data_path: Annotated[FilePath, Depends(get_data_path)]) -> ProjectsList:
    projects_list = ProjectsList(
        projects=[get_project_files(project_dir) for project_dir in data_path.iterdir() if project_dir.is_dir()]
    )
    projects_list.projects.sort(key=lambda x: x.name.lower())
    return projects_list


def get_profanity_list_model() -> ProfanityList:
    return ProfanityList(word_list=get_profanity_list())


def dir_copy(src: FilePath, dst: FilePath):
    for root, dirs, files in src.walk():
        for file in files:
            with open(root / file, "rb") as fd:
                with open(dst / file, "wb") as tfd:
                    tfd.write(fd.read())
        for directory in dirs:
            (dst / directory).mkdir(parents=True)
            dir_copy(root / directory, dst / directory)


def convert_to_title_case(word: str) -> str:
    """Converts a word or phrase to title case"""
    return word.title()


def get_a_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_api_key(ws: WebSocket) -> str:
    return ws.state.config.ai.api_key


def get_ai_model(key: Annotated[str, Depends(get_api_key)], ws: WebSocket) -> AnthropicModel:
    return AnthropicModel(
        model_name=ws.state.config.ai.model,
        provider=AnthropicProvider(api_key=key),
    )


def get_topic_agent(model: Annotated[AnthropicModel, Depends(get_ai_model)]) -> Agent:
    return Agent(
        model=model,
        instructions="""
Respond in the role of word search puzzle book author.

Following these strict rules:
1. Topic-specific sub-topics only - Every word must relate specifically to the main topic. No generic filler sub-topics.
2. Maximum 40 characters per sub-topic - Example: "Flying Scotsman" = 16 characters.
3. No profanity or offensive language - Proper names are always acceptable regardless of potential alternative meanings (e.g., "Billy Connolly" is fine).
5. No word/phrase in the wordlist may contain numbers - No entries like "A4 Pacific", "B17", "11th September" etc. Find alternatives without numbers.
6. No word/phrase in the wordlist may contain punctuation, except for hyphen "-" and space " " - No entries like "Scottish, Castle" or "Scottish! Castle".
7. No word/phrase in the wordlist may contain roman numerals - No entries contain sub-strings like "I", "II", "III", "IV", "V", etc or words/phrases like "King George V", "James VI". Find alternatives without roman numerals.
8. Every puzzle must be unique - No duplication or near duplication of subtopics. Don't have both "Scottish Castles" and "Historic Scottish Fortresses".
9. Use UK English - British spelling and terminology throughout (colour, honour, recognise, localise, etc.).
10. Sub-topics should be presented in title case (capitalize first letter of each word, lowercase the rest) and avoid contractions.
11. The book title must end with the words "Word Search Puzzles".
12. The front page introduction should be engaging and informative, and should not exceed 200 words.
13. The front page introduction should include a brief overview of the topic and its significance.
14. the front page introduction should include a call to action to play the puzzles - for example "So, grab a pen and prepare to explore the bonnie banks and heather-clad moors".

Each response should consist of a book title for the main topic, a front page introduction to the topic, and a list of subtopics of the length specified.
""",
        output_type=WordlistInput,
        tools=[convert_to_title_case, get_a_timestamp],
        output_retries=3,
    )


def get_puzzle_input_agent(model: Annotated[AnthropicModel, Depends(get_ai_model)]) -> Agent:
    return Agent(
        model=model,
        instructions="""
Respond in the role of word search puzzle book author.

Following these strict rules:
1. Topic-specific words/phrases only in the wordlist - Every word must relate specifically to the topic and subtopic.
2. Words/phrases should NOT be generic filler words like "traditional", "famous", "popular", "beautiful" etc.
3. Minimum of 4 and maximum of 20 characters per word/phrase (excluding spaces) in the wordlist - Count only letters and punctuation, not spaces. Example: "Flying Scotsman" = 15 characters (excluding the space).
4. Remove repetitive words from subtopic context - If the subtopic is "Scottish Castles," don't include "Castle" in each entry. "Edinburgh Castle" becomes just "Edinburgh." If the subtopic is "Scottish Lochs," "Loch Ness" becomes just "Ness."
5. No profanity or offensive language - Proper names are always acceptable regardless of potential alternative meanings (e.g., "Billy Connolly" is fine).
6. No word/phrase in the wordlist may contain numbers - No entries like "A4 Pacific", "B17", "11th September" etc. Find alternatives without numbers.
7. No word/phrase in the wordlist may contain punctuation, except for hyphen "-" and space " " - No entries like "Scottish, Castle" or "Scottish! Castle".
8. No word/phrase in the wordlist may contain roman numerals - No entries contain sub-strings like "I", "II", "III", "IV", "V", etc or words/phrases like "King George V", "James VI". Find alternatives without roman numerals.
9. Words/phrases in wordlist should be presented in title case (capitalize first letter of each word, lowercase the rest) and avoid contractions.
10. Use UK English - British spelling and terminology throughout (colour, honour, recognise, localise, etc.).
11. Introduction should be engaging and informative, providing a brief overview of the subtopic. It should not exceed 250 words. It should not require and context from the did you know fact.
12. Did you know fact should be engaging, informative and if possible amusing, citing a little known fact about the subtopic. It should not exceed 25 words. It should not require and context from the introduction.

Each response should include a wordlist with the specified number of entries, a short introduction paragraph, and a did you know fact.
""",
        output_type=PuzzleInput,
        tools=[convert_to_title_case, get_a_timestamp],
        output_retries=5,
    )
