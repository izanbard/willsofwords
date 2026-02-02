from datetime import datetime

import pytest
from pydantic import ValidationError

from backend.models.wordlist import PuzzleInput, Wordlist

from ...utils import get_profanity_list
from ..test_utils import TestUtils


class TestCategory(TestUtils):
    @pytest.fixture
    def valid_category_data(self):
        return {
            "puzzle_topic": "Animals",
            "word_list": ["Cat", "Dog", "Elephant"],
            "introduction": "Animals are diverse and critical to ecosystems.",
            "did_you_know": "Animals are vital.",
        }

    def test_category_initialization_valid(self, valid_category_data):
        category = PuzzleInput(**valid_category_data)
        assert category.puzzle_topic == "Animals"
        assert category.word_list == ["Cat", "Dog", "Elephant"]
        assert category.introduction == "Animals are diverse and critical to ecosystems."

    def test_category_initialization_invalid_length(self, valid_category_data):
        valid_category_data["puzzle_topic"] = "An"  # Less than 3 characters
        with pytest.raises(ValidationError):
            PuzzleInput(**valid_category_data)

    def test_category_check_profanity(self, profanity_mocks, logger_mock):

        category_data = {
            "puzzle_topic": "Category with BADWORD",
            "word_list": ["Clean word", "BADWORD", "Another BADWORD", "More"],
            "introduction": "This contains a BADWORD.",
            "did_you_know": "No profanity here.",
        }
        category = PuzzleInput(**category_data)
        result = category.check_profanity()
        assert logger_mock.call_count == 4
        assert result == ["BADWORD", "BADWORD.", "BADWORD", "BADWORD"]

    def test_category_check_for_illegal_chars(self, valid_category_data):
        valid_category_data["word_list"] = ["Cat", "D&g", "Eleph@nt"]
        with pytest.raises(ValidationError):
            PuzzleInput(**valid_category_data)


class TestWordlist(TestUtils):
    @pytest.fixture
    def mock_category(self, mocker):
        return mocker.Mock(
            PuzzleInput,
            puzzle_topic="Animals",
            check_for_illegal_chars=mocker.Mock(return_value=[]),
            check_profanity=mocker.Mock(return_value=[]),
        )

    @pytest.fixture
    def valid_wordlist_data(self, mock_category):
        return {
            "topic": "Test Wordlist",
            "title": "Test Wordlist",
            "creation_date": datetime.now().isoformat(),
            "front_page_introduction": "This is a test introduction.",
            "did_you_know": "This is a test did you know.",
            "categories": [mock_category, mock_category],
        }

    def test_wordlist_initialization_valid(self, valid_wordlist_data):
        wordlist = Wordlist(**valid_wordlist_data)
        assert wordlist.title == "Test Wordlist"
        assert len(wordlist.categories) == 2

    def test_wordlist_initialization_invalid_title_length(self, valid_wordlist_data):
        valid_wordlist_data["title"] = "AB"
        with pytest.raises(ValidationError):
            Wordlist(**valid_wordlist_data)

    def test_wordlist_check_profanity(self, profanity_mocks, logger_mock, mock_category):
        wordlist = Wordlist(
            topic="Topic BADWORD", title="Title BADWORD", front_page_introduction="", categories=[mock_category]
        )
        result = wordlist.check_profanity()
        assert logger_mock.call_count == 2
        assert result == ["BADWORD", "BADWORD"]

    def test_wordlist_validate_word_lists(self, profanity_mocks, logger_mock, mock_category):

        wordlist = Wordlist(
            topic="Topic BADWORD", title="Title BADWORD", front_page_introduction="", categories=[mock_category]
        )
        result = wordlist.validate_word_lists()
        assert logger_mock.call_count == 2
        mock_category.check_for_illegal_chars.assert_called()
        assert result == {"illegal_chars": [], "profanity": ["BADWORD", "BADWORD"]}

    def test_wordlist_profanity_list_retrieval(self):
        assert Wordlist.profanity_list() == get_profanity_list()
