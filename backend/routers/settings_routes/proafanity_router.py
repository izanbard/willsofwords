import string
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models import ProfanityList
from backend.routers import get_profanity_list_model
from backend.utils import get_profanity_list

ProfanityRouter = APIRouter(
    prefix="/profanity",
    tags=["Settings"],
)


@ProfanityRouter.get(
    path="/",
    response_model=ProfanityList,
    summary="Get the list of profanity words.",
    description="Returns a list of profanity words.",
    response_description="A list of profanity words.",
    status_code=status.HTTP_200_OK,
)
async def profanity_list(profanity_model: Annotated[ProfanityList, Depends(get_profanity_list_model)]) -> ProfanityList:
    return profanity_model


@ProfanityRouter.put(
    path="/",
    response_model=ProfanityList,
    summary="Add a profanity word.",
    description="Adds a profanity word to the list.",
    response_description="The updated list of profanity words.",
    status_code=status.HTTP_200_OK,
)
async def add_profanity_word(
    word: str, profanity_model: Annotated[ProfanityList, Depends(get_profanity_list_model)]
) -> ProfanityList:
    if len(word) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word cannot be empty.")
    word = word.strip().upper().translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation})
    if word in profanity_model.word_list:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Word already exists in list.")
    profanity_model.word_list.append(word)
    profanity_model.save_profanity_list(FilePath("backend/assets/profanity.txt"))
    return ProfanityList(word_list=get_profanity_list())


@ProfanityRouter.post(
    path="/",
    response_model=ProfanityList,
    summary="replace entire profanity list with new list",
    description="replace entire profanity list with new list",
    status_code=status.HTTP_200_OK,
)
async def replace_profanity_list(new_list: ProfanityList) -> ProfanityList:
    if not all(isinstance(word, str) for word in new_list.word_list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All list items must be strings.")
    new_list.word_list = [
        x.strip().upper().translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation})
        for x in new_list.word_list
    ]
    new_list.save_profanity_list(FilePath("backend/assets/profanity.txt"))
    return ProfanityList(word_list=get_profanity_list())


@ProfanityRouter.delete(
    path="/",
    response_model=ProfanityList,
    summary="Remove a profanity word.",
    description="Removes a profanity word from the list.",
    status_code=status.HTTP_200_OK,
)
async def remove_profanity_word(
    word: str, profanity_model: Annotated[ProfanityList, Depends(get_profanity_list_model)]
) -> ProfanityList:
    word = word.strip().upper().translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation})
    if word not in profanity_model.word_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found in list.")
    profanity_model.word_list.remove(word)
    profanity_model.save_profanity_list(FilePath("backend/assets/profanity.txt"))
    return profanity_model
