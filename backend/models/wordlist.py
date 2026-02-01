import re
import string
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path as FilePath

from pydantic import BaseModel, Field, field_validator

from backend.utils import Logger, get_profanity_list


class WordlistBase(BaseModel, ABC):
    """
    Abstract base class that serves as a foundation for implementing profanity
    filtering functionality in subclasses.

    This class outlines the structure for subclasses to implement specific methods
    for checking profanity in text inputs. It also includes utility methods to
    validate a word list against a predefined profanity list and provides access
    to a common profanity list.
    """

    @abstractmethod
    def check_profanity(self):
        raise NotImplementedError("This method must be implemented by subclasses")

    def _check_word_list(self, word_list: list[str]):
        """
        Validates a list of words to check for the presence of profanity using a predefined
        profanity list. Logs a warning if any profane word is detected.

        :param word_list: A list of words to be validated.
        :type word_list: list[str]
        """
        profanity = []
        for word in word_list:
            if word.upper().strip(string.whitespace + string.punctuation) in self.profanity_list():
                profanity.append(word)
                Logger.get_logger().warn(f"Validating Input: Profanity found in word: {word}")

        return profanity

    @staticmethod
    def profanity_list() -> list[str]:
        """
        Retrieves the predefined profanity list for validation purposes.

        :return: A list of profane words.
        :rtype: list[str]
        """
        return get_profanity_list()


class PuzzleInput(WordlistBase):
    """
    Represents a category containing a title, facts, and a list of associated words.

    This class serves as a structured way to handle data for a specific category.
    Each category includes a title, a long descriptive fact, a short descriptive
    fact, and a list of associated words that can be validated for profanity and
    illegal characters. This ensures consistency and correctness in category data.

    :ivar puzzle_topic: The title of the category. Must be between 3 and 80 characters.
    :type puzzle_topic: str
    :ivar word_list: The list of words associated with this category. Each word
        must be between 3 and 75 characters.
    :type word_list: list[str]
    :ivar introduction: The long fact of the category, providing a detailed description.
    :type introduction: str
    :ivar did_you_know: The short fact of the category, providing a brief description.
    :type did_you_know: str
    """

    puzzle_topic: str = Field(description="The title", min_length=3, max_length=80)
    word_list: list[str] = Field(description="the list of words for this category", min_length=3, max_length=75)
    introduction: str = Field(..., description="Introduction to the puzzle topic, should be engaging and informative")
    did_you_know: str = Field(..., description="Short fact about the puzzle topic, should be concise and informative")

    @field_validator("introduction", mode="after")
    @classmethod
    def check_introduction_length(cls, value):
        if len(value.split()) > 250:
            raise ValueError("Introduction should be less than 250 words")
        return value

    @field_validator("did_you_know", mode="after")
    @classmethod
    def check_did_you_know_length(cls, value):
        if len(value.split()) > 25:
            raise ValueError("Did you know fact should be less than 25 words")
        return value

    @field_validator("word_list", mode="after")
    @classmethod
    def check_word_list_length(cls, value):
        exp = re.compile(
            r"\b(?:XC|XL|LX{0,3}|X{1,3})(?:IX|IV|VI{0,3}|I{1,3})\b|\b(?:XC|XL|LX{0,3}|X{1,3})\b|\b(?:IX|IV|VI{0,3}|I{1,3})\b"
        )
        for word in value:
            for char in word:
                if not (char.isascii() and char.isalpha() or char == " " or char == "-"):
                    raise ValueError(
                        f"Words in the wordlist must not contain numbers or punctuation.  {word} violates this rule, please try again"
                    )
            if exp.search(word):
                raise ValueError(
                    f"Words in the wordlist must not contain roman numerals. {word} violates this rule, please try again"
                )
        return value

    def check_profanity(self):
        """
        Checks for profane content within text fields of a given instance.

        This method invokes a private word-checking utility on specific text fields
        associated with the instance, ensuring none of the words or phrases contain
        profanity. It processes multiple fields, including categories, long facts,
        short facts, and phrases within a predefined word list.

        :param self: Refers to the instance of the class for which the method is being called.

        :return: None
        """
        profanity = (
            self._check_word_list(self.puzzle_topic.split())
            + self._check_word_list(self.introduction.split())
            + self._check_word_list(self.did_you_know.split())
        )
        for phrase in self.word_list:
            profanity += self._check_word_list(phrase.split())
        return profanity

    def check_for_illegal_chars(self):
        """
        Checks the word list for illegal characters.

        This method iterates through each word in the word list and every character
        in each word, ensuring that they are valid. A valid character is ASCII,
        alphabetic, a space, or a hyphen. If an illegal character is encountered,
        a ValueError is raised with details about the offending word and its
        category.

        :raises ValueError:
            If any illegal character is found in a word within the word list.
        """
        illegal_chars = []
        for word in self.word_list:
            for char in word:
                if not (char.isascii() and char.isalpha() or char == " " or char == "-"):
                    illegal_chars.append(char)
                    Logger.get_logger().warn(
                        f"Validating Input: Illegal character found in word: {self.puzzle_topic} - {word}"
                    )
        return illegal_chars


class WordlistInput(WordlistBase):
    topic: str = Field(description="The topic of the book of puzzles as provided by the user", min_length=3, max_length=80)
    title: str = Field(description="The title of the book to be used on the front page and cover", min_length=3, max_length=80)
    creation_date: str = Field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds"), description="The date the word list was created"
    )
    front_page_introduction: str = Field(
        ..., description="Introduction to the book of puzzles, should be engaging and informative"
    )
    subtopic_list: list[str] = Field([], description="the list of subtopics to be used for the puzzle book")

    def check_profanity(self):
        profanity = self._check_word_list(self.title.split())
        profanity += self._check_word_list(self.topic.split())
        profanity += self._check_word_list(self.front_page_introduction.split())
        return profanity


class Wordlist(WordlistBase):
    topic: str = Field(description="The topic of the book of puzzles as provided by the user", min_length=3, max_length=80)
    title: str = Field(description="The title of the book to be used on the front page and cover", min_length=3, max_length=80)
    creation_date: str = Field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds"), description="The date the word list was created"
    )
    front_page_introduction: str = Field(
        ..., description="Introduction to the book of puzzles, should be engaging and informative"
    )
    categories: list[PuzzleInput] = Field(description="The category list")

    def check_profanity(self):
        """
        Checks all text-based attributes and nested categories for instances of profanity.

        This method splits and evaluates specific text attributes of the object for
        inappropriate language using the `_check_word_list` method. Additionally, it
        iterates through all objects in the `categories` and invokes their
        `check_profanity` method.

        :raises ValueError: If any profane words are detected in the text attributes.
        """
        profanity = self._check_word_list(self.title.split())
        profanity += self._check_word_list(self.topic.split())
        profanity += self._check_word_list(self.front_page_introduction.split())
        for category in self.categories:
            profanity += category.check_profanity()
        return profanity

    def validate_word_lists(self):
        """
        Validates word lists by checking for profanity and ensuring no illegal characters
        exist in the provided categories.

        This function performs a dual validation process: it runs a profanity check
        and iterates through a list of categories, where each category is subjected
        to a character legality check.

        :raises ValueError: Raised if profanity or illegal characters are detected during
            the validation process.
        :return: A dictionary with keys 'profanity' and 'illegal_chars' indicating validation results.
        """
        profanity = self.check_profanity()
        illegal_char_list = []
        for category in self.categories:
            illegal_char_list += category.check_for_illegal_chars()
        return {"profanity": profanity, "illegal_chars": illegal_char_list}

    def save_wordlist(self, filename: FilePath):
        with open(filename, "w") as fd:
            fd.write(self.model_dump_json(indent=2))
