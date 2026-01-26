from math import ceil

import pytest

from backend.models.grid_size import GridSize, ProjectConfig

from ..test_utils import TestUtils


class TestGridSize(TestUtils):
    @pytest.fixture
    def rows(self):
        return 10

    @pytest.fixture
    def columns(self):
        return 10

    @pytest.fixture
    def puzzle_config(self, mocker, rows, columns):
        return mocker.Mock(ProjectConfig, max_rows=rows, max_columns=columns)

    def test_grid_size_exceeds_max_dimensions(self, puzzle_config, rows, columns):
        len_words = 200
        max_density = 0.1
        grid = GridSize(project_config=puzzle_config, len_words=len_words, max_density=max_density)

        assert grid.rows == rows
        assert grid.columns == columns

    def test_grid_size_exact_square(self, puzzle_config):
        len_words = 25
        max_density = 1.0
        grid = GridSize(project_config=puzzle_config, len_words=len_words, max_density=max_density)

        assert grid.rows == 5
        assert grid.columns == 5

    def test_grid_size_non_square_fitting(self, puzzle_config):
        len_words = 10
        max_density = 0.5
        grid = GridSize(project_config=puzzle_config, len_words=len_words, max_density=max_density)

        target_size = ceil(len_words / max_density)
        assert grid.rows * grid.columns >= target_size
        assert grid.rows == 5
        assert grid.columns == 4

    def test_grid_size_low_max_density(self, puzzle_config, rows, columns):
        len_words = 47
        max_density = 0.5
        grid = GridSize(project_config=puzzle_config, len_words=len_words, max_density=max_density)

        target_size = ceil(len_words / max_density)
        assert grid.rows * grid.columns >= target_size
        assert grid.rows == rows
        assert grid.columns == columns
