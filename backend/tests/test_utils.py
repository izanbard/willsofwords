import pytest

from backend.models import ProjectConfig
from backend.utils import create_default_files, get_project_settings_defaults


class TestUtils:

    @pytest.fixture(autouse=True)
    def setup(self):
        create_default_files()

    @pytest.fixture
    def project_config(self):
        return ProjectConfig(**get_project_settings_defaults())

    @pytest.fixture
    def bad_words(self):
        return ["BADWORD"]

    @pytest.fixture
    def profanity_mocks(self, mocker, bad_words):
        profanity_check = mocker.patch("backend.models.wordlist.WordlistBase.profanity_list", return_value=bad_words)
        return profanity_check

    @pytest.fixture
    def logger_mock(self, mocker):
        mock_warn = mocker.Mock()
        mocker.patch("backend.utils.Logger.get_logger", return_value=mocker.Mock(warn=mock_warn))
        return mock_warn
