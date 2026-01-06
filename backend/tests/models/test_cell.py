import pytest
from backend.models.cell import Cell
from backend.models.enums import DirectionEnum


class TestCell:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.direction = DirectionEnum.EW
        self.value = "B"

    @pytest.fixture
    def cell_instance(self):
        return Cell(loc_x=0, loc_y=0, is_answer=False)

    def test_str_returns_value_of_cell(self, cell_instance):
        cell_instance.set_answer(value=self.value, direction=self.direction)
        result = str(cell_instance)
        assert result == self.value

    def test_str_returns_default_value_of_cell(self, cell_instance):
        result = str(cell_instance)
        assert result == "."

    def test_set_answer_updates_value_and_direction(self, cell_instance):
        cell_instance.set_answer(value=self.value, direction=self.direction)
        assert cell_instance.value == self.value
        assert cell_instance.is_answer is True
        assert cell_instance.direction[self.direction] is True

    def test_set_answer_does_not_overwrite_other_directions(self, cell_instance):
        cell_instance.direction[DirectionEnum.NESW] = True
        cell_instance.set_answer(value=self.value, direction=self.direction)
        assert cell_instance.value == self.value
        assert cell_instance.is_answer is True
        assert cell_instance.direction[DirectionEnum.NESW] is True
        assert cell_instance.direction[self.direction] is True
