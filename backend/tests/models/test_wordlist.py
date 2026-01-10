from datetime import datetime

import pytest
from backend.models.wordlist import Category, Wordlist
from pydantic import ValidationError
from ...utils import get_profanity_list
from ..test_utils import TestUtils


class TestCategory(TestUtils):

    def test_category_initialization_valid(self):
        category_data = {
            "category": "Animals",
            "word_list": ["Cat", "Dog", "Elephant"],
            "long_fact": "Animals are diverse and critical to ecosystems.",
            "short_fact": "Animals are vital.",
        }
        category = Category(**category_data)

        assert category.category == "Animals"
        assert category.word_list == ["Cat", "Dog", "Elephant"]
        assert category.long_fact == "Animals are diverse and critical to ecosystems."
        assert category.short_fact == "Animals are vital."

    def test_category_initialization_invalid_length(self):
        category_data = {
            "category": "An",  # Less than 3 characters
            "word_list": ["Cat", "Dog", "Elephant"],
            "long_fact": "Animals are diverse and critical to ecosystems.",
            "short_fact": "Animals are vital.",
        }
        with pytest.raises(ValidationError):
            Category(**category_data)

    def test_category_check_profanity(self, mocker):
        profanity_check = mocker.patch("backend.models.wordlist.WordlistBase.profanity_list", return_value=["BADWORD"])
        mock_warn = mocker.Mock()
        mocker.patch("backend.utils.Logger.get_logger", return_value=mocker.Mock(warn=mock_warn))
        category_data = {
            "category": "Category with BADWORD",
            "word_list": ["Clean word", "BADWORD", "Another BADWORD", "More"],
            "long_fact": "This contains a BADWORD.",
            "short_fact": "No profanity here.",
        }
        category = Category(**category_data)

        category.check_profanity()

        profanity_check.assert_called()
        mock_warn.assert_called()
        assert mock_warn.call_count == 4

    def test_category_check_for_illegal_chars(self):
        category_data = {
            "category": "Animals",
            "word_list": ["Cat", "Dog", "Eleph@nt"],
            "long_fact": "Animals are diverse and critical to ecosystems.",
            "short_fact": "Animals are vital.",
        }
        category = Category(**category_data)

        with pytest.raises(ValueError) as exc_info:
            category.check_for_illegal_chars()

        assert "Illegal character found in word: Animals - Eleph@nt" in str(exc_info.value)


class TestWordlist(TestUtils):
    @pytest.fixture
    def mock_category(self, mocker):
        return mocker.Mock(Category, category="Animals", check_for_illegal_chars=mocker.Mock(return_value=None))

    def test_wordlist_initialization_valid(self, mock_category):
        wordlist_data = {
            "title": "Test Wordlist",
            "category_prompt": "List of categories",
            "wordlist_prompt": "Words to include in the wordlist",
            "creation_date": datetime.now(),
            "category_list": [mock_category, mock_category],
        }
        wordlist = Wordlist(**wordlist_data)

        assert wordlist.title == "Test Wordlist"
        assert len(wordlist.category_list) == 2
        assert wordlist.category_list[0].category == "Animals"

    def test_wordlist_initialization_invalid_title_length(self):
        wordlist_data = {
            "title": "AB",  # Less than 3 characters
            "category_prompt": "Prompt text",
            "wordlist_prompt": "Prompt text",
            "creation_date": datetime.now(),
            "category_list": [],
        }
        with pytest.raises(ValidationError):
            Wordlist(**wordlist_data)

    def test_wordlist_check_profanity(self, mocker, mock_category):
        profanity_check = mocker.patch("backend.models.wordlist.WordlistBase.profanity_list", return_value=["BADWORD"])
        mock_warn = mocker.Mock()
        mocker.patch("backend.utils.Logger.get_logger", return_value=mocker.Mock(warn=mock_warn))

        wordlist_data = {
            "title": "Title containing BADWORD",
            "category_prompt": "Something CLEAN",
            "wordlist_prompt": "Another BADWORD here",
            "creation_date": datetime.now(),
            "category_list": [mock_category],
        }
        wordlist = Wordlist(**wordlist_data)

        wordlist.check_profanity()

        profanity_check.assert_called()
        mock_warn.assert_called()
        assert mock_warn.call_count == 2

    def test_wordlist_validate_word_lists(self, mocker, mock_category):
        profanity_check = mocker.patch("backend.models.wordlist.WordlistBase.profanity_list", return_value=["BADWORD"])
        mock_warn = mocker.Mock()
        mocker.patch("backend.utils.Logger.get_logger", return_value=mocker.Mock(warn=mock_warn))
        wordlist_data = {
            "title": "Title containing BADWORD",
            "category_prompt": "Something CLEAN",
            "wordlist_prompt": "Another BADWORD here",
            "creation_date": datetime.now(),
            "category_list": [mock_category, mock_category],
        }
        wordlist = Wordlist(**wordlist_data)
        wordlist.validate_word_lists()
        profanity_check.assert_called()
        mock_warn.assert_called()
        assert mock_warn.call_count == 2
        mock_category.check_for_illegal_chars.assert_called()

    def test_test_wordlist_profanity_list(self):
        assert Wordlist.profanity_list() == get_profanity_list()
