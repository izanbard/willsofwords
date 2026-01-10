import string
from abc import abstractmethod, ABC
from datetime import datetime
from pydantic import BaseModel, Field

from backend.utils import get_profanity_list, Logger


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
        for word in word_list:
            if word.upper().strip(string.whitespace + string.punctuation) in self.profanity_list():
                Logger.get_logger().warn(f"Validating Input: Profanity found in word: {word}")

    @staticmethod
    def profanity_list() -> list[str]:
        """
        Retrieves the predefined profanity list for validation purposes.

        :return: A list of profane words.
        :rtype: list[str]
        """
        return get_profanity_list()


class Category(WordlistBase):
    """
    Represents a category containing a title, facts, and a list of associated words.

    This class serves as a structured way to handle data for a specific category.
    Each category includes a title, a long descriptive fact, a short descriptive
    fact, and a list of associated words that can be validated for profanity and
    illegal characters. This ensures consistency and correctness in category data.

    :ivar category: The title of the category. Must be between 3 and 80 characters.
    :type category: str
    :ivar word_list: The list of words associated with this category. Each word
        must be between 3 and 75 characters.
    :type word_list: list[str]
    :ivar long_fact: The long fact of the category, providing a detailed description.
    :type long_fact: str
    :ivar short_fact: The short fact of the category, providing a brief description.
    :type short_fact: str
    """

    category: str = Field(description="The title", min_length=3, max_length=80)
    word_list: list[str] = Field(description="the list of words for this category", min_length=3, max_length=75)
    long_fact: str = Field(description="The long fact of the category")
    short_fact: str = Field(description="The short fact of the category")

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
        self._check_word_list(self.category.split())
        self._check_word_list(self.long_fact.split())
        self._check_word_list(self.short_fact.split())
        for phrase in self.word_list:
            self._check_word_list(phrase.split())

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
        for word in self.word_list:
            for char in word:
                if not (char.isascii() and char.isalpha() or char == " " or char == "-"):
                    raise ValueError(f"Validating Input: Illegal character found in word: {self.category} - {word}")


class Wordlist(WordlistBase):
    """
    Represents a word list with associated metadata and functionality to validate and
    check for profanity within its elements.

    This class is used to manage word lists with associated categories. It includes
    functionality to validate and clean up various elements within the word list,
    ensuring compliance with defined profanity and character constraints.

    :ivar title: The title of the word list, with a minimum length of 3 characters
        and a maximum length of 80 characters.
    :type title: str
    :ivar category_prompt: The prompt used to retrieve the category list.
    :type category_prompt: str
    :ivar wordlist_prompt: The prompt used to retrieve the word list.
    :type wordlist_prompt: str
    :ivar creation_date: The date the word list was created. Defaults to the current
        datetime at the time of instantiation.
    :type creation_date: datetime
    :ivar category_list: The list of categories associated with the word list.
    :type category_list: list[Category]
    """

    title: str = Field(description="The title", min_length=3, max_length=80)
    category_prompt: str = Field(description="The prompt used to get the category list")
    wordlist_prompt: str = Field(description="The prompt used to get the word list")
    creation_date: datetime = Field(default_factory=datetime.now, description="The date the word list was created")
    category_list: list[Category] = Field(description="The category list")

    def check_profanity(self):
        """
        Checks all text-based attributes and nested categories for instances of profanity.

        This method splits and evaluates specific text attributes of the object for
        inappropriate language using the `_check_word_list` method. Additionally, it
        iterates through all objects in the `category_list` and invokes their
        `check_profanity` method.

        :raises ValueError: If any profane words are detected in the text attributes.
        """
        self._check_word_list(self.title.split())
        self._check_word_list(self.category_prompt.split())
        self._check_word_list(self.wordlist_prompt.split())
        for category in self.category_list:
            category.check_profanity()

    def validate_word_lists(self):
        """
        Validates word lists by checking for profanity and ensuring no illegal characters
        exist in the provided categories.

        This function performs a dual validation process: it runs a profanity check
        and iterates through a list of categories, where each category is subjected
        to a character legality check.

        :raises ValueError: Raised if profanity or illegal characters are detected during
            the validation process.
        :return: None
        """
        self.check_profanity()
        for category in self.category_list:
            category.check_for_illegal_chars()
