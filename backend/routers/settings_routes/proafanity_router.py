import string

from fastapi import APIRouter, status, HTTPException

from backend.models import ProfanityList
from backend.utils import get_profanity_list, save_profanity_list

ProfanityRouter = APIRouter(
    prefix="/profanity",
    tags=["settings"],
)


@ProfanityRouter.get(
    path="/",
    response_model=ProfanityList,
    summary="Get the list of profanity words.",
    description="Returns a list of profanity words.",
    response_description="A list of profanity words.",
    status_code=status.HTTP_200_OK,
)
async def profanity_list() -> ProfanityList:
    return ProfanityList(word_list=get_profanity_list())


@ProfanityRouter.put(
    path="/",
    response_model=ProfanityList,
    summary="Add a profanity word.",
    description="Adds a profanity word to the list.",
    response_description="The updated list of profanity words.",
    status_code=status.HTTP_200_OK,
)
async def add_profanity_word(word: str) -> ProfanityList:
    if len(word) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Word cannot be empty.")
    word_list = get_profanity_list()
    word = word.strip().upper().translate({ord(c): None for c in string.whitespace + string.digits + string.punctuation})
    if word in word_list:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Word already exists in list.")
    word_list.append(word)
    save_profanity_list(word_list)
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
    save_profanity_list(new_list.word_list)
    return ProfanityList(word_list=get_profanity_list())


@ProfanityRouter.delete(
    path="/",
    response_model=ProfanityList,
    summary="Remove a profanity word.",
    description="Removes a profanity word from the list.",
    status_code=status.HTTP_200_OK,
)
async def remove_profanity_word(word: str) -> ProfanityList:
    word_list = get_profanity_list()
    word = word.strip().upper()
    if word not in word_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found in list.")
    word_list.remove(word)
    save_profanity_list(word_list)
    return ProfanityList(word_list=get_profanity_list())
