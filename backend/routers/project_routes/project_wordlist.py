from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from backend.models import Wordlist
from backend.routers import (
    check_wordlist_exists,
    get_wordlist_path,
    load_wordlist,
    validate_word_lists,
)

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
async def get_wordlist(wordlist: Annotated[Wordlist, Depends(load_wordlist)]) -> Wordlist:
    return wordlist


@ProjectWordlistRouter.post(
    "/",
    summary="Update the named project wordlist",
    description="Updates the project wordlist",
    status_code=status.HTTP_200_OK,
    response_description="The updated project wordlist.",
)
async def update_wordlist(new_wordlist: Wordlist, wordlist_path: Annotated[FilePath, Depends(get_wordlist_path)]) -> Wordlist:
    new_wordlist = validate_word_lists(new_wordlist)
    new_wordlist.save_wordlist(wordlist_path)
    return new_wordlist


@ProjectWordlistRouter.delete(
    "/",
    summary="Delete the named project wordlist",
    description="Deletes the project wordlist",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wordlist(wordlist_path: Annotated[FilePath, Depends(check_wordlist_exists)]) -> None:
    wordlist_path.unlink()
    return None
