from datetime import datetime
from pydantic import BaseModel, Field


class Category(BaseModel):
    category: str = Field(description="The title of the category", min_length=3, max_length=80)
    word_list: list[str] = Field(description="the list of words for this category", min_length=3, max_length=75)
    long_fact: str = Field(description="The long fact of the category")
    short_fact: str = Field(description="The short fact of the category")


class Wordlist(BaseModel):
    title: str = Field(description="The title of the Wordlist", min_length=3, max_length=80)
    category_prompt: str = Field(description="The prompt used to get the category list")
    wordlist_prompt: str = Field(description="The prompt used to get the word list")
    creation_date: datetime = Field(default_factory=datetime.now, description="The date the word list was created")
    category_list: list[Category] = Field(description="The category list")
