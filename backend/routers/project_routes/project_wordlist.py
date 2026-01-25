import json
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from starlette import status
from starlette.requests import Request


from backend.models import Wordlist
from backend.utils import sanitise_user_input_path

ProjectWordlistRouter = APIRouter(
    prefix="/wordlist",
    tags=["Project"],
)


@ProjectWordlistRouter.get(
    "/",
    summary="Get the named project wordlist",
    description="Returns the project wordlist",
    response_description="The project wordlist.",
    status_code=status.HTTP_200_OK,
)
async def get_wordlist(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request) -> Wordlist:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    wordlist_path = data_dir / req.state.config.app.input_filename
    if not wordlist_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} wordlist not found")
    with open(wordlist_path, "r") as fd:
        return Wordlist(**json.load(fd))


@ProjectWordlistRouter.post(
    "/",
    summary="Update the named project wordlist",
    description="Updates the project wordlist",
    status_code=status.HTTP_200_OK,
    response_description="The updated project wordlist.",
)
async def update_wordlist(
    name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], wordlist: Wordlist, req: Request
) -> Wordlist:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    validation_dict = wordlist.validate_word_lists()
    if validation_dict["profanity"] or validation_dict["illegal_chars"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wordlist contains invalid words. Profanity: {validation_dict['profanity']}, Illegal Chars: {validation_dict['illegal_chars']}",
        )
    wordlist_path = data_dir / req.state.config.app.input_filename
    with open(wordlist_path, "w") as fd:
        json.dump(wordlist.model_dump(), fd, indent=2)
    return wordlist


@ProjectWordlistRouter.delete(
    "/",
    summary="Delete the named project wordlist",
    description="Deletes the project wordlist",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wordlist(name: Annotated[str, Path(min_length=1, regex=r"^[a-zA-Z0-9_-]+$")], req: Request) -> None:
    name = sanitise_user_input_path(name)
    data_dir = FilePath(req.state.config.app.data_folder) / name
    if not data_dir.exists() or not data_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {name} not found")
    wordlist_path = data_dir / req.state.config.app.input_filename
    if wordlist_path.exists():
        wordlist_path.unlink()
    return None
