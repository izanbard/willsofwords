import bisect
import random
import string
from math import ceil

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field
from profanity_check import predict_prob
from .config import Config
from src.models import DirectionEnum, Cell
from ..utils import Logger


class Puzzle(BaseModel):
    puzzle_title: str = Field(..., description="the title of the puzzle")
    input_word_list: list[str] = Field(..., description="the words supplied to this puzzle for creation")
    height: int = Field(..., description="the height of the board in cells", ge=0)
    width: int = Field(..., description="the width of the board in cells", ge=0)
    cells: list[list[Cell]] = Field(
        default_factory=lambda data: [[Cell(loc_y=h, loc_x=w) for w in range(data["width"])] for h in range(data["height"])],
        description="the cells of the board",
    )
    puzzle_word_list: list[str] = Field(default_factory=list, description="the words used in this puzzle")
    density: float = Field(default=0.0, description="the density of words in the puzzle")
    profanity: dict[str, int] = Field(
        default_factory=dict, description="the profanity of scores for rows/cols/diags in puzzle"
    )

    def _get_density(self) -> None:
        if len(self.puzzle_word_list) == 0:
            return
        self.density = self.calculate_density(self.height, self.width, self._occupied_cell_count())

    def puzzle_reset(self):
        self.cells = [[Cell(loc_y=h, loc_x=w) for w in range(self.width)] for h in range(self.height)]
        self.puzzle_word_list = []
        self.density = 0
        self.profanity = {}

    def change_puzzle_size(self, height: int, width: int):
        self.height = height
        self.width = width
        self.puzzle_reset()

    def populate_puzzle(self):
        attempts = 0
        while (
            attempts < Config.MAX_PLACEMENT_ATTEMPTS
            and self.density < Config.MAX_PUZZLE_DENSITY
            and len(self.puzzle_word_list) < len(self.input_word_list)
        ):
            word: str = random.choice(list(set(self.input_word_list) - set(self.puzzle_word_list)))
            Logger.get_logger().debug(f"placing word {word}")
            if word in self.puzzle_word_list:
                continue
            if self.place_a_word(word.replace(" ", "").upper()):
                Logger.get_logger().debug(f"successfully placed {word}")
                bisect.insort_left(self.puzzle_word_list, word)
                self._get_density()
            else:
                Logger.get_logger().debug(f"failed to place {word}, trying again (will get another word form input)")
            attempts += 1
        self._fill_empty_cells()
        Logger.get_logger().debug("Puzzle made, checking for profanity")
        self.check_for_inadvertent_profanity()

    def place_a_word(self, word: str) -> bool:
        direction = self._get_direction(word)
        Logger.get_logger().debug(f"placing word {word} direction {direction}")
        word_reversed = random.choice([True, False])
        if word_reversed:
            Logger.get_logger().debug(f"placing word {word} reversed")
            word = word[::-1]

        match direction:
            case DirectionEnum.EW:
                row = random.randint(0, self.height - 1)
                col = random.randint(0, self.width - len(word))
                space_available = all(
                    (
                        not self.cells[row][c].is_answer
                        or (self.cells[row][c].value == word[i] and self.cells[row][c].direction != direction)
                    )
                    for i, c in enumerate(range(col, col + len(word)))
                )
                if space_available:
                    for i, c in enumerate(range(col, col + len(word))):
                        self.cells[row][c].set_answer(value=word[i], direction=direction)
                    return True
            case DirectionEnum.NWSE:
                row = random.randint(0, self.height - len(word))
                col = random.randint(0, self.width - len(word))

                space_available = all(
                    (
                        not self.cells[r][c].is_answer
                        or (self.cells[r][c].value == word[i] and self.cells[r][c].direction != direction)
                    )
                    for i, (r, c) in enumerate(zip(range(row, row + len(word)), range(col, col + len(word))))
                )
                if space_available:
                    for i, (r, c) in enumerate(zip(range(row, row + len(word)), range(col, col + len(word)))):
                        self.cells[r][c].set_answer(value=word[i], direction=DirectionEnum(direction))
                    return True
            case DirectionEnum.NS:
                row = random.randint(0, self.height - len(word))
                col = random.randint(0, self.width - 1)
                space_available = all(
                    (
                        not self.cells[r][col].is_answer
                        or (self.cells[r][col].value == word[i] and self.cells[r][col].direction != direction)
                    )
                    for i, r in enumerate(range(row, row + len(word)))
                )
                if space_available:
                    for i, r in enumerate(range(row, row + len(word))):
                        self.cells[r][col].set_answer(value=word[i], direction=DirectionEnum(direction))
                    return True
            case DirectionEnum.NESW:
                row = random.randint(len(word) - 1, self.height - 1)
                col = random.randint(0, self.width - len(word))
                space_available = all(
                    (
                        not self.cells[r][c].is_answer
                        or (self.cells[r][c].value == word[i] and self.cells[r][c].direction != direction)
                    )
                    for i, (r, c) in enumerate(zip(range(row, row - len(word), -1), range(col, col + len(word))))
                )
                if space_available:
                    for i, (r, c) in enumerate(zip(range(row, row - len(word), -1), range(col, col + len(word)))):
                        self.cells[r][c].set_answer(value=word[i], direction=DirectionEnum(direction))
                    return True
        return False

    def _get_direction(self, word: str) -> DirectionEnum | None:
        possible_directions = self._get_possible_directions(word)
        if len(possible_directions) == 0:
            return None
        direction = random.choice(possible_directions)
        return direction

    def _get_possible_directions(self, word: str) -> list[str]:
        possible_directions = list(DirectionEnum)
        if len(word) > min(self.height, self.width):
            possible_directions.remove(DirectionEnum.NWSE)
            possible_directions.remove(DirectionEnum.NESW)
        if len(word) > self.height:
            possible_directions.remove(DirectionEnum.NS)
        if len(word) > self.width:
            possible_directions.remove(DirectionEnum.EW)
        return possible_directions

    def _fill_empty_cells(self):
        for row in self.cells:
            for cell in row:
                if not cell.is_answer:
                    cell.value = random.choice(string.ascii_uppercase)

    def _occupied_cell_count(self):
        count = 0
        for row in self.cells:
            for cell in row:
                if cell.is_answer:
                    count += 1
        return count

    def create_board_image(self, width_in_pixels: int, image_type: str = "puzzle"):
        cell_size = ceil((width_in_pixels - 50) / self.width)
        base_board = Image.new("LA", (width_in_pixels, (cell_size * self.height) + 50), color=(127, 255))
        for row in self.cells:
            for cell in row:
                if image_type == "puzzle":
                    tile_image = cell.create_puzzle_tile_image(cell_size)
                elif image_type == "solution":
                    tile_image = cell.create_solution_tile_image(cell_size)
                else:
                    raise ValueError(f"Unknown type {image_type}")
                base_board.paste(tile_image, ((cell.loc_x * cell_size) + 25, (cell.loc_y * cell_size) + 25))
        return base_board

    def check_for_inadvertent_profanity(self):
        grid_strings: dict[str, str] = self._get_grid_strings()
        for name, grid_string in grid_strings.items():
            grid_string_substrings_forward = [
                grid_string[i:j] for i in range(len(grid_string)) for j in range(i + 1, len(grid_string) + 1)
            ]
            gird_string_substrings_backward = [
                grid_string[-j:-i:-1] for i in range(1, len(grid_string) + 1) for j in range(i + 1, len(grid_string) + 2)
            ]
            predictions = predict_prob(grid_string_substrings_forward + gird_string_substrings_backward)
            max_prediction = max(predictions)
            self.profanity[name] = max_prediction

    def _get_grid_strings(self) -> dict[str, str]:
        return_strings: dict[str, str] = {}
        lattice = np.empty((self.height, self.width), dtype=str)
        for row in self.cells:
            for cell in row:
                lattice[cell.loc_y, cell.loc_x] = cell.value
        for y in range(self.height):
            return_strings["row" + str(y)] = "".join(lattice[y, :])
        for x in range(self.width):
            return_strings["col" + str(x)] = "".join(lattice[:, x])
        for j in range(-self.height + 1, self.width):
            return_strings["nwse" + str(j)] = "".join(lattice.diagonal(j))
            return_strings["nesw" + str(j)] = "".join(np.flipud(lattice).diagonal(j))
        return return_strings

    @staticmethod
    def calculate_density(height: int, width: int, solution_count: int) -> float:
        total_area = height * width
        density = solution_count / total_area
        return density
