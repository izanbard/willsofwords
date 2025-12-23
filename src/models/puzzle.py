import bisect
import random
import string
from math import ceil

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field
from profanity_check import predict_prob
from .config import Config
from src.models import DirectionEnum, Cell
from .enums import BoardImageEnum
from ..utils import Logger


class Puzzle(BaseModel):
    puzzle_title: str = Field(..., description="the title of the puzzle")
    input_word_list: list[str] = Field(..., description="the words supplied to this puzzle for creation")
    rows: int = Field(..., description="the height of the board in cells", ge=0)
    columns: int = Field(..., description="the width of the board in cells", ge=0)
    cells: list[list[Cell]] = Field(
        default_factory=lambda data: [[Cell(loc_y=h, loc_x=w) for w in range(data["columns"])] for h in range(data["rows"])],
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
        self.density = self.calculate_density(self.rows, self.columns, self._occupied_cell_count())

    def puzzle_reset(self):
        self.cells = [[Cell(loc_y=h, loc_x=w) for w in range(self.columns)] for h in range(self.rows)]
        self.puzzle_word_list = []
        self.density = 0
        self.profanity = {}

    def change_puzzle_size(self, height: int, width: int):
        self.rows = height
        self.columns = width
        self.puzzle_reset()

    def populate_puzzle(self):
        attempts = 0
        while (
            attempts < Config.PUZZLE_MAX_PLACEMENT_ATTEMPTS
            and self.density < Config.PUZZLE_MAX_DENSITY
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
        if Config.PUZZLE_ENABLE_PROFANITY_FILTER:
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

    def _calculate_cells_size(self) -> int:
        cell_size_by_width = int(Config.PRINT_GRID_WIDTH / self.columns)
        cell_size_by_height = int(Config.PRINT_GRID_HEIGHT / self.rows)
        if cell_size_by_width < Config.PRINT_MIN_CELL_SIZE:
            return Config.PRINT_MIN_CELL_SIZE
        if cell_size_by_width > Config.PRINT_MAX_CELL_SIZE:
            if cell_size_by_height < Config.PRINT_MIN_CELL_SIZE:
                return Config.PRINT_MIN_CELL_SIZE
            if cell_size_by_height > Config.PRINT_MAX_CELL_SIZE:
                return Config.PRINT_MAX_CELL_SIZE
            return cell_size_by_height
        if cell_size_by_height < Config.PRINT_MIN_CELL_SIZE:
            return cell_size_by_width
        if cell_size_by_height > Config.PRINT_MAX_CELL_SIZE:
            return cell_size_by_width
        return min(cell_size_by_height, cell_size_by_width)

    def content_image_count(self) -> int:
        cell_size = self._calculate_cells_size()
        if cell_size * self.rows <= Config.PRINT_GRID_HEIGHT:
            return 1
        if cell_size * self.rows < Config.PRINT_GRID_HEIGHT_TWO_PAGE:
            return 2
        raise ValueError("You fucked this, wills, you moron")

    def _create_title_block(self) -> Image.Image:
        title = Image.new("LA", (Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_TITLE_BOX_HEIGHT_PIXELS), color=(0, 0))
        draw = ImageDraw.Draw(title)
        draw.text(
            (title.width // 2, title.height // 2),
            self.puzzle_title,
            fill=(0, 255),
            font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_TITLE_FONT_SIZE),
            anchor="mm",
        )
        return title

    def create_wordlist_image(self, two_page: bool = False):
        if two_page:
            wordlist = Image.new(
                "LA",
                (
                    Config.PRINT_CONTENT_WIDTH_PIXELS,
                    (Config.PRINT_CONTENT_HEIGHT_PIXELS - Config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2,
                ),
                color=(0, 0),
            )
        else:
            wordlist = Image.new(
                "LA", (Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS), color=(0, 0)
            )
        font = ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_WORDLIST_FONT_SIZE)
        draw = ImageDraw.Draw(wordlist)
        t, _, _, b = draw.textbbox(
            xy=(0, 0),
            text=self.puzzle_word_list[0],
            font=font,
        )
        line_height = b - t
        max_sublist_length = int(wordlist.height / (line_height + Config.PRINT_WORDLIST_LINE_SPACING_PIXELS))
        number_of_groups = max(ceil(len(self.puzzle_word_list) / max_sublist_length), 3)
        chunk_size = ceil(len(self.puzzle_word_list) / number_of_groups)
        chunk_image_list = []
        for n in range(0, len(self.puzzle_word_list), chunk_size):
            chunk_dimensions = draw.multiline_textbbox(
                xy=(0, 0), text="\n".join(self.puzzle_word_list[n : n + chunk_size]), font=font
            )
            chunk = Image.new("LA", (ceil(chunk_dimensions[2]), ceil(chunk_dimensions[3])), color=(0, 0))
            draw2 = ImageDraw.Draw(chunk)
            draw2.multiline_text(
                xy=(0, 0),
                text="\n".join(self.puzzle_word_list[n : n + chunk_size]),
                font=font,
                align="center",
                fill=(0, 255),
            )
            chunk_image_list.append(chunk)
        if number_of_groups % 2 == 1:
            middle = len(chunk_image_list) // 2
            left_edge = wordlist.width // 2 - chunk_image_list[middle].width // 2
            right_edge = wordlist.width // 2 + chunk_image_list[middle].width // 2
            wordlist.paste(chunk_image_list[middle], (left_edge, 0), chunk_image_list[middle])
            for n in range(middle - 1, -1, -1):
                left_edge = left_edge - chunk_image_list[n].width
                wordlist.paste(chunk_image_list[n], (left_edge, 0), chunk_image_list[n])
            for n in range(middle + 1, len(chunk_image_list), 1):
                wordlist.paste(chunk_image_list[n], (right_edge, 0), chunk_image_list[n])
                right_edge = right_edge + chunk_image_list[n].width
        return wordlist

    def create_page_content(self) -> list[Image.Image]:
        content = Image.new("LA", (Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_CONTENT_HEIGHT_PIXELS), color=(0, 0))
        title = self._create_title_block()
        board = self.create_board_image(BoardImageEnum.PUZZLE)
        content.paste(title, (0, 0), title)
        content.paste(board, (content.width // 2 - board.width // 2, Config.PRINT_TITLE_BOX_HEIGHT_PIXELS), board)
        content2 = None
        if self.content_image_count() == 2:
            content2 = Image.new("LA", (Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_CONTENT_HEIGHT_PIXELS), color=(0, 0))
            content2.paste(title, (0, 0), title)
            wordlist = self.create_wordlist_image(two_page=True)
            content2.paste(
                wordlist, (content2.width // 2 - wordlist.width // 2, Config.PRINT_TITLE_BOX_HEIGHT_PIXELS), wordlist
            )
        else:
            wordlist = self.create_wordlist_image()
            content.paste(
                wordlist,
                (content.width // 2 - wordlist.width // 2, content.height - Config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS),
                wordlist,
            )
        return [i for i in [content, content2] if i is not None]

    def create_board_image(self, image_type: BoardImageEnum = BoardImageEnum.PUZZLE) -> Image.Image:
        cell_size = self._calculate_cells_size()
        grid = Image.new("LA", ((cell_size * self.columns), (cell_size * self.rows)), color=(0, 0))
        for row in self.cells:
            for cell in row:
                if image_type == BoardImageEnum.PUZZLE:
                    tile_image = cell.create_puzzle_tile_image(cell_size)
                elif image_type == BoardImageEnum.SOLUTION:
                    tile_image = cell.create_solution_tile_image(cell_size)
                else:
                    raise ValueError(f"Unknown type {image_type}")
                grid.paste(tile_image, ((cell.loc_x * cell_size), (cell.loc_y * cell_size)))
        board = Image.new(
            "LA",
            (
                grid.width + Config.PRINT_GRID_MARGIN_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_PAD_PIXELS,
                grid.height + Config.PRINT_GRID_MARGIN_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_PAD_PIXELS,
            ),
            color=(0, 0),
        )
        draw = ImageDraw.Draw(board)
        draw.rounded_rectangle(
            [
                (0 + Config.PRINT_GRID_PAD_PIXELS, 0 + Config.PRINT_GRID_PAD_PIXELS),
                (board.width - Config.PRINT_GRID_PAD_PIXELS, board.height - Config.PRINT_GRID_PAD_PIXELS),
            ],
            radius=Config.PRINT_GRID_BORDER_RADIUS,
            fill=(0, 0),
            outline=(0, 255),
            width=Config.PRINT_GRID_BORDER_PIXELS,
        )
        board.paste(grid, (((board.width // 2) - grid.width // 2), ((board.height // 2) - grid.height // 2)), grid)
        return board

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
        lattice = np.empty((self.rows, self.columns), dtype=str)
        for row in self.cells:
            for cell in row:
                lattice[cell.loc_y, cell.loc_x] = cell.value
        for y in range(self.rows):
            return_strings["row" + str(y)] = "".join(lattice[y, :])
        for x in range(self.columns):
            return_strings["col" + str(x)] = "".join(lattice[:, x])
        for j in range(-self.rows + 1, self.columns):
            return_strings["nwse" + str(j)] = "".join(lattice.diagonal(j))
            return_strings["nesw" + str(j)] = "".join(np.flipud(lattice).diagonal(j))
        return return_strings

    @staticmethod
    def calculate_density(height: int, width: int, solution_count: int) -> float:
        total_area = height * width
        density = solution_count / total_area
        return density
