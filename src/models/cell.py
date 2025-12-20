from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field

from src.models import DirectionEnum


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

    def create_puzzle_tile_image(self, size_in_pixels: int):
        base = Image.new("LA", (size_in_pixels, size_in_pixels), color=(255, 255))
        draw = ImageDraw.Draw(base)
        draw.text(
            (size_in_pixels / 2, size_in_pixels / 2),
            text=self.value,
            fill=(0, 255),
            font=ImageFont.truetype("src/assets/verdana.ttf", size=size_in_pixels / 2),
            anchor="mm",
        )
        return base

    def create_solution_tile_image(self, size_in_pixels: int):
        base = self.create_puzzle_tile_image(size_in_pixels)
        draw = ImageDraw.Draw(base)
        if self.direction[DirectionEnum.NS]:
            draw.line(
                ((size_in_pixels / 2, 0), (size_in_pixels / 2, size_in_pixels)), fill=(0, 255), width=int(size_in_pixels / 10)
            )
        if self.direction[DirectionEnum.EW]:
            draw.line(
                ((0, size_in_pixels / 2), (size_in_pixels, size_in_pixels / 2)), fill=(0, 255), width=int(size_in_pixels / 10)
            )
        if self.direction[DirectionEnum.NESW]:
            draw.line(((0, size_in_pixels), (size_in_pixels, 0)), fill=(0, 255), width=int(size_in_pixels / 10))
        if self.direction[DirectionEnum.NWSE]:
            draw.line(((0, 0), (size_in_pixels, size_in_pixels)), fill=(0, 255), width=int(size_in_pixels / 10))
        return base

    def __str__(self):
        return self.value
