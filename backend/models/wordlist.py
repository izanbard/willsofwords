from abc import abstractmethod
from datetime import datetime
from pydantic import BaseModel, Field

from backend.utils import get_profanity_list, Logger


class WordlistBase(BaseModel):
    @abstractmethod
    def check_profanity(self):
        raise NotImplementedError("This method must be implemented by subclasses")

    @staticmethod
    def _check_word_list(word_list: list[str]):
        for word in word_list:
            if word.upper() in get_profanity_list():
                Logger.get_logger().warn(f"Validating Input: Profanity found in word: {word}")


class Category(WordlistBase):
    category: str = Field(description="The title", min_length=3, max_length=80)
    word_list: list[str] = Field(description="the list of words for this category", min_length=3, max_length=75)
    long_fact: str = Field(description="The long fact of the category")
    short_fact: str = Field(description="The short fact of the category")

    def check_profanity(self):
        self._check_word_list(self.category.split())
        self._check_word_list(self.long_fact.split())
        self._check_word_list(self.short_fact.split())
        for phrase in self.word_list:
            self._check_word_list(phrase.split())

    def check_for_illegal_chars(self):
        for word in self.word_list:
            for char in word:
                if not (char.isascii() and char.isalpha() or char == " " or char == "-"):
                    raise ValueError(f"Validating Input: Illegal character found in word: {self.category} - {word}")


class Wordlist(WordlistBase):
    title: str = Field(description="The title", min_length=3, max_length=80)
    category_prompt: str = Field(description="The prompt used to get the category list")
    wordlist_prompt: str = Field(description="The prompt used to get the word list")
    creation_date: datetime = Field(default_factory=datetime.now, description="The date the word list was created")
    category_list: list[Category] = Field(description="The category list")

    def check_profanity(self):
        self._check_word_list(self.title.split())
        self._check_word_list(self.category_prompt.split())
        self._check_word_list(self.wordlist_prompt.split())
        for category in self.category_list:
            category.check_profanity()

    def validate_word_lists(self):
        self.check_profanity()
        for category in self.category_list:
            category.check_for_illegal_chars()
