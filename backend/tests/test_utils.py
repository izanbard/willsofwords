import pytest
from backend.utils import create_env_file_if_not_exists


class TestUtils:

    @pytest.fixture(autouse=True)
    def setup(self):
        create_env_file_if_not_exists()
