from pydantic import BaseModel, Field

from .enums import DirectionEnum


class Cell(BaseModel):
    """
    Represents a single cell in a grid-based puzzle.

    This class defines a cell with specific attributes such as its position within
    a grid, its value, whether it is part of an answer, and the directions of any
    answers passing through the cell. It provides functionality to update the cell
    to be part of an answer.

    :ivar loc_x: The x position of the cell within the grid.
    :type loc_x: int
    :ivar loc_y: The y position of the cell within the grid.
    :type loc_y: int
    :ivar value: The character representing the cell's content.
    :type value: str
    :ivar is_answer: Indicates whether the cell is part of an answer in the puzzle.
    :type is_answer: bool
    :ivar direction: A dictionary indicating the presence of answers passing through
        the cell in each direction.
    :type direction: dict[DirectionEnum, bool]
    """

    loc_x: int = Field(description="The x position of the cell", ge=0)
    loc_y: int = Field(description="The y position of the cell", ge=0)
    value: str = Field(default=".", description="The letter of the cell", max_length=1, min_length=1)
    is_answer: bool = Field(default=False, description="Whether the cell is part of an answer")
    direction: dict[DirectionEnum, bool] = Field(
        default_factory=lambda: dict.fromkeys(list(DirectionEnum), False),
        description="The direction of any answers passing through the cell",
    )

    def set_answer(self, value: str, direction: DirectionEnum) -> None:
        """
        Sets the answer's value and marks the answer as valid. Updates the given
        direction to reflect the change.

        :param value: The value to set as the answer.
        :type value: str
        :param direction: The direction to be updated after the answer is set.
        :type direction: DirectionEnum
        :return: None
        """
        self.value = value
        self.is_answer = True
        self.direction[direction] = True

    def __str__(self):
        """
        Provides a string representation of the instance by returning its value.

        :return: String representation of the instance
        :rtype: str
        """
        return self.value
