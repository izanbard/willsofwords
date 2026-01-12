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
