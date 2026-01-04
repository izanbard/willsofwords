from pydantic import BaseModel, Field

from .enums import DirectionEnum


class Cell(BaseModel):
    loc_x: int = Field(description="The x position of the cell", ge=0)
    loc_y: int = Field(description="The y position of the cell", ge=0)
    value: str = Field(default=".", description="The letter of the cell", max_length=1, min_length=1)
    is_answer: bool = Field(default=False, description="Whether the cell is part of an answer")
    direction: dict[DirectionEnum, bool] = Field(
        default_factory=lambda: dict.fromkeys(list(DirectionEnum), False),
        description="The direction of any answers passing through the cell",
    )

    def set_answer(self, value: str, direction: DirectionEnum) -> None:
        self.value = value
        self.is_answer = True
        self.direction[direction] = True

    def __str__(self):
        return self.value
