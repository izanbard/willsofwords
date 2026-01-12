from math import ceil

import pytest

from PIL import Image
from backend.models import BoardImageEnum, DirectionEnum
from backend.pages import SubContentsCell
from ..test_utils import TestUtils


class TestSubContentsCell(TestUtils):
    """Test class for SubContentsCell"""

    @pytest.fixture
    def mock_cell(self, mocker):
        return mocker.Mock(
            value="X",
            direction={
                DirectionEnum.NS: False,
                DirectionEnum.EW: True,
                DirectionEnum.NESW: False,
                DirectionEnum.NWSE: True,
            },
        )

    @pytest.fixture
    def cell_size(self):
        return 50

    @pytest.fixture
    def puzzle_grid_type(self):
        return BoardImageEnum.PUZZLE

    @pytest.fixture
    def solution_grid_type(self):
        return BoardImageEnum.SOLUTION

    @pytest.fixture
    def instance_puzzle(self, mock_cell, cell_size, puzzle_grid_type, project_config):
        return SubContentsCell(cell=mock_cell, cell_size=cell_size, grid_type=puzzle_grid_type, project_config=project_config)

    @pytest.fixture
    def instance_solution(self, mock_cell, cell_size, solution_grid_type, project_config):
        return SubContentsCell(
            cell=mock_cell, cell_size=cell_size, grid_type=solution_grid_type, project_config=project_config
        )

    @pytest.fixture
    def solution_cell_size(self, cell_size):
        return (
            cell_size + ceil((cell_size / 10) / 2 * 1.42),
            cell_size + ceil((cell_size / 10) / 2 * 1.42),
        )

    def test_initialization_puzzle(self, instance_puzzle, cell_size):
        assert instance_puzzle.cell is not None
        assert instance_puzzle.size == (cell_size, cell_size)
        assert instance_puzzle.grid_type == BoardImageEnum.PUZZLE
        assert isinstance(instance_puzzle.base_image, Image.Image)
        assert instance_puzzle.base_image.size == (cell_size, cell_size)

    def test_initialization_solution(self, instance_solution, solution_cell_size):
        assert instance_solution.size == solution_cell_size
        assert instance_solution.grid_type == BoardImageEnum.SOLUTION

    def test_get_content_image_puzzle(self, instance_puzzle, cell_size):
        image = instance_puzzle.get_content_image()
        assert isinstance(image, Image.Image)
        assert image.size == (cell_size, cell_size)

    def test_get_content_image_solution_with_drawing(self, instance_solution, solution_cell_size):
        image = instance_solution.get_content_image()
        assert isinstance(image, Image.Image)
        assert image.size == solution_cell_size
