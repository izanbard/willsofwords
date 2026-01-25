import bisect
import random

import numpy as np

from pydantic import BaseModel, Field
from .cell import Cell
from .enums import LayoutEnum, DirectionEnum
from .project_config import ProjectConfig
from backend.utils import Logger, get_profanity_list


class Puzzle(BaseModel):
    project_config: ProjectConfig = Field(..., description="Configuration for puzzle generation")
    puzzle_id: str = Field(
        ..., description="the unique id (within this book context) of the puzzle formed from the puzzle title"
    )
    puzzle_title: str = Field(..., description="the title of the puzzle")
    display_title: str = Field(default="", description="the display title of the puzzle")
    input_word_list: list[str] = Field(..., description="the words supplied to this puzzle for creation")
    long_fact: str = Field(default="", description="the long fact of the puzzle")
    short_fact: str = Field(default="", description="the short fact of the puzzle")
    rows: int = Field(..., description="the height of the board in cells", ge=0)
    columns: int = Field(..., description="the width of the board in cells", ge=0)
    cells: list[list[Cell]] = Field(
        default_factory=lambda data: [[Cell(loc_y=h, loc_x=w) for w in range(data["columns"])] for h in range(data["rows"])],
        description="the cells of the board",
    )
    puzzle_search_list: list[str] = Field(default_factory=list, description="the words used in this puzzle")
    density: float = Field(default=0.0, description="the density of words in the puzzle")
    profanity: dict[str, list[tuple[str, tuple[str, int, int]]]] = Field(
        default_factory=dict, description="the profanity of scores for rows/cols/diags in puzzle"
    )

    def _get_density(self) -> None:
        if len(self.puzzle_search_list) == 0:
            return
        self.density = self.calculate_density(self.rows, self.columns, self._occupied_cell_count())

    def puzzle_reset(self):
        self.cells = [[Cell(loc_y=h, loc_x=w) for w in range(self.columns)] for h in range(self.rows)]
        self.puzzle_search_list = []
        self.density = 0
        self.profanity = {}

    def reset_profanity(self):
        self.profanity = {}
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                self.cells[y][x].is_profane = False

    def change_puzzle_size(self, height: int, width: int):
        self.rows = height
        self.columns = width
        self.puzzle_reset()

    def populate_puzzle(self):
        attempts = 0
        while (
            attempts < self.project_config.max_placement_attempts
            and self.density < self.project_config.max_density
            and len(self.puzzle_search_list) < len(self.input_word_list)
        ):
            word: str = random.choice(list(set(self.input_word_list) - set(self.puzzle_search_list))).upper()
            Logger.get_logger().debug(f"placing word {word}")
            if word in self.puzzle_search_list:
                continue
            if self.place_a_word(word.replace(" ", "").replace("-", "").upper()):
                Logger.get_logger().debug(f"successfully placed {word}")
                bisect.insort_left(self.puzzle_search_list, word)
                self._get_density()
            else:
                Logger.get_logger().debug(f"failed to place {word}, trying again (will get another word form input)")
            attempts += 1
        self._fill_empty_cells()
        Logger.get_logger().debug("Puzzle made, checking for profanity")

    def place_a_word(self, word: str) -> bool:
        direction = self._get_direction(word)
        Logger.get_logger().debug(f"placing word {word} direction {direction}")
        word_reversed = random.choice([True, False])
        if word_reversed:
            Logger.get_logger().debug(f"placing word {word} reversed")
            word = word[::-1]

        match direction:
            case DirectionEnum.EW:
                row = random.randint(0, self.rows - 1)
                col = random.randint(0, self.columns - len(word))
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
                row = random.randint(0, self.rows - len(word))
                col = random.randint(0, self.columns - len(word))

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
                row = random.randint(0, self.rows - len(word))
                col = random.randint(0, self.columns - 1)
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
                row = random.randint(len(word) - 1, self.rows - 1)
                col = random.randint(0, self.columns - len(word))
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
        if len(word) > min(self.rows, self.columns):
            possible_directions.remove(DirectionEnum.NWSE)
            possible_directions.remove(DirectionEnum.NESW)
        if len(word) > self.rows:
            possible_directions.remove(DirectionEnum.NS)
        if len(word) > self.columns:
            possible_directions.remove(DirectionEnum.EW)
        return possible_directions

    def get_random_letters(self):
        weighted_letters = {
            "E": 12.7,
            "T": 9.1,
            "A": 8.2,
            "O": 7.5,
            "I": 7.0,
            "N": 6.7,
            "S": 6.3,
            "H": 6.1,
            "R": 6.0,
            "D": 4.3,
            "L": 4.0,
            "C": 2.8,
            "U": 2.8,
            "M": 2.4,
            "W": 2.4,
            "F": 2.2,
            "G": 2.0,
            "Y": 2.0,
            "P": 1.9,
            "B": 1.5,
            "V": 0.98,
            "K": 0.77,
            "J": 0.16,
            "X": 0.15,
            "Q": 0.12,
            "Z": 0.074,
        }
        total_cells = self.rows * self.columns
        occupied = self._occupied_cell_count()
        random_list = random.choices(
            population=list(weighted_letters.keys()), weights=list(weighted_letters.values()), k=total_cells - occupied
        )
        return random_list

    def _fill_empty_cells(self):
        random_list = self.get_random_letters()
        for row in self.cells:
            for cell in row:
                if not cell.is_answer:
                    cell.value = random_list.pop()

    def _occupied_cell_count(self):
        count = 0
        for row in self.cells:
            for cell in row:
                if cell.is_answer:
                    count += 1
        return count

    def get_puzzle_layout(self) -> LayoutEnum:
        if 0 < self.rows <= self.project_config.medium_rows:
            return LayoutEnum.SINGLE
        if self.project_config.medium_rows < self.rows <= self.project_config.max_rows:
            return LayoutEnum.DOUBLE
        raise ValueError("You fucked this, wills, you moron")

    def check_for_inadvertent_profanity(self):
        self.reset_profanity()
        grid_strings: dict[str, list[tuple[str, tuple[int, int]]]] = self._get_grid_strings()
        for name, grid_string in grid_strings.items():
            grid_string_substrings_forward = self._check_grid_string(grid_string)
            gird_string_substrings_backward = self._check_grid_string(grid_string[::-1], "R")
            if len(grid_string_substrings_forward) > 0:
                for coord_list in [x[2] for x in grid_string_substrings_forward]:
                    for coord in coord_list:
                        self.cells[coord[1]][coord[0]].is_profane = True
            if len(gird_string_substrings_backward) > 0:
                for coord_list in [x[2] for x in gird_string_substrings_backward]:
                    for coord in coord_list:
                        self.cells[coord[1]][coord[0]].is_profane = True
            bad_words = [(x[0], x[1]) for x in grid_string_substrings_forward] + [
                (x[0], x[1]) for x in gird_string_substrings_backward
            ]
            if len(bad_words) > 0:
                self.profanity[name] = bad_words

    def _check_grid_string(
        self, grid_string: list[tuple[str, tuple[int, int]]], direction: str = "F"
    ) -> list[tuple[str, tuple[str, int, int], list[tuple[int, int]]]]:
        ret_var = []
        for i in range(len(grid_string)):
            for j in range(i + 1, len(grid_string) + 1):
                word = "".join(letter[0] for letter in grid_string[i:j])
                if self._check_a_word_against_profanity_list(word):
                    ret_var.append((word, (direction, i, j), [letter[1] for letter in grid_string[i:j]]))
        return ret_var

    @staticmethod
    def _check_a_word_against_profanity_list(word: str) -> bool:
        return word in get_profanity_list()

    def _get_grid_strings(self) -> dict[str, list[tuple[str, tuple[int, int]]]]:
        return_strings: dict[str, list[tuple[str, tuple[int, int]]]] = {}
        lattice = np.empty((self.rows, self.columns), dtype=object)
        for row in self.cells:
            for cell in row:
                lattice[cell.loc_y, cell.loc_x] = (cell.value, (cell.loc_x, cell.loc_y))
        for y in range(self.rows):
            return_strings[f"row{y}"] = [(x[0], x[1]) for x in lattice[y, :]]
        for x in range(self.columns):
            return_strings[f"col{x}"] = [(x[0], x[1]) for x in lattice[:, x]]
        for j in range(-self.rows + 1, self.columns):
            nwse_cords = f"0-{-j}" if j <= 0 else f"{j}-0"
            nesw_cords = f"0-{self.rows + j}" if j <= 0 else f"{j}-{self.rows}"
            return_strings[f"nwse{nwse_cords}"] = [(x[0], x[1]) for x in lattice.diagonal(j)]
            return_strings[f"swne{nesw_cords}"] = [(x[0], x[1]) for x in np.flipud(lattice).diagonal(j)]
        return return_strings

    @staticmethod
    def calculate_density(height: int, width: int, solution_count: int) -> float:
        total_area = height * width
        density = solution_count / total_area
        return density


class PuzzleLetter(BaseModel):
    letter: str = Field(..., description="the letter of the puzzle", min_length=1, max_length=1)
