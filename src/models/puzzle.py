import bisect
import random
import string
from math import ceil

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageText
from pydantic import BaseModel, Field
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
    profanity: dict[str, list[str]] = Field(
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
            word: str = random.choice(list(set(self.input_word_list) - set(self.puzzle_word_list))).upper()
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
        if not Config.PRINT_VARIABLE_CELL_SIZE:
            return Config.PRINT_MIN_CELL_SIZE
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

    def _create_title_block(self, puzzle_number: int) -> Image.Image:
        title = Image.new("LA", (Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_TITLE_BOX_HEIGHT_PIXELS), color=(0, 0))
        draw = ImageDraw.Draw(title)
        draw.text(
            (title.width // 2, title.height // 2),
            str(puzzle_number) + ". " + self.puzzle_title,
            fill=(0, 255),
            font=ImageFont.truetype("src/assets/verdana-bold.ttf", size=Config.PRINT_TITLE_FONT_SIZE),
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
        font_size = Config.PRINT_WORDLIST_FONT_SIZE - 1
        exceeds_size = [True]
        draw = ImageDraw.Draw(wordlist)
        while any(exceeds_size):
            font_size -= 1
            font = ImageFont.truetype("src/assets/verdana.ttf", size=font_size)
            line_height_calculate_text = ImageText.Text(text=self.puzzle_word_list[0], font=font)
            line_height = int(line_height_calculate_text.get_bbox()[3])
            max_sublist_length = int(wordlist.height / (line_height + Config.PRINT_WORDLIST_LINE_SPACING_PIXELS))
            number_of_groups = max(ceil(len(self.puzzle_word_list) / max_sublist_length), 3)
            chunk_size = ceil(len(self.puzzle_word_list) / number_of_groups)
            group_width = Config.PRINT_CONTENT_WIDTH_PIXELS / number_of_groups
            texts: list[ImageText.Text] = []
            for group_number in range(number_of_groups):
                text = ImageText.Text(
                    "\n".join(self.puzzle_word_list[group_number * chunk_size : (group_number * chunk_size) + chunk_size]),
                    font=font,
                )
                texts.append(text)
            exceeds_size = [x.get_bbox()[2] > group_width for x in texts]
        for group_number in range(number_of_groups):
            draw.multiline_text(
                xy=(int(group_number * group_width) + (group_width // 2), 0),
                text=texts[group_number],
                align="left",
                anchor="ma",
                fill=(0, 255),
                spacing=Config.PRINT_WORDLIST_LINE_SPACING_PIXELS,
            )
        if Config.PRINT_DEBUG:
            wordlist = wordlist.convert("RGBA")
            draw = ImageDraw.Draw(wordlist)
            for group_number in range(1, number_of_groups):
                draw.line(
                    [(int(group_number * group_width), 0), (int(group_number * group_width), wordlist.height)],
                    fill=(51, 153, 255, 255),
                    width=2,
                )
        return wordlist

    def create_did_you_know(self):
        did_you_know = Image.new(
            "LA",
            (
                Config.PRINT_CONTENT_WIDTH_PIXELS,
                (Config.PRINT_CONTENT_HEIGHT_PIXELS - Config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2,
            ),
            color=(0, 0),
        )
        draw = ImageDraw.Draw(did_you_know)
        title = ImageText.Text(
            text="Did you know?",
            font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_CELL_FONT_SIZE_PIXELS * 2),
        )
        draw.text((0, 0), text=title, fill=(0, 255))
        placeholder_lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ut lacinia diam. Nunc lacus est, vulputate euismod eros eget, accumsan tempor lectus. Nam feugiat massa mi, vitae dictum nisl porta vitae. Vestibulum quis sapien at orci placerat posuere. Praesent in magna auctor, convallis lectus nec, vestibulum ligula. Integer aliquet odio turpis, quis efficitur tellus finibus at. Mauris non auctor mi. Suspendisse bibendum sit amet elit ut dapibus. Phasellus commodo, ex sed rutrum rutrum, nunc nibh scelerisque massa, eu pretium nisi nunc id nibh. Suspendisse potenti. Donec eu vulputate mauris. Integer et molestie arcu."
        split_list = []
        temp_list = []
        for word in placeholder_lorem.split():
            line = ImageText.Text(
                text=" ".join(temp_list + [word]),
                font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_CELL_FONT_SIZE_PIXELS),
            )
            if line.get_length() < Config.PRINT_CONTENT_WIDTH_PIXELS:
                temp_list.append(word)
            else:
                split_list.append(temp_list)
                temp_list = [word]
        paragraph = ImageText.Text(
            "\n".join([" ".join(x) for x in split_list]),
            font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_CELL_FONT_SIZE_PIXELS),
        )
        draw.text(
            (0, int(title.get_bbox()[3])),
            paragraph,
            fill=(0, 255),
            align="left",
            spacing=Config.PRINT_WORDLIST_LINE_SPACING_PIXELS,
        )
        return did_you_know

    def create_page_content(self, puzzle_number: int) -> list[Image.Image]:
        content = Image.new("LA", (Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_CONTENT_HEIGHT_PIXELS), color=(0, 0))
        title = self._create_title_block(puzzle_number)
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
            did_you_know = self.create_did_you_know()
            content2.paste(
                did_you_know,
                (
                    0,
                    ((Config.PRINT_CONTENT_HEIGHT_PIXELS - Config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2)
                    + Config.PRINT_TITLE_BOX_HEIGHT_PIXELS,
                ),
                did_you_know,
            )
        else:
            wordlist = self.create_wordlist_image()
            content.paste(
                wordlist,
                (content.width // 2 - wordlist.width // 2, content.height - Config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS),
                wordlist,
            )
        return [i for i in [content, content2] if i is not None]

    def create_solution_page_content(self, puzzle_number: int):
        title = self._create_title_block(puzzle_number)
        board = self.create_board_image(BoardImageEnum.SOLUTION)
        content = Image.new("LA", (Config.PRINT_CONTENT_WIDTH_PIXELS + 10, title.height + board.height + 10), color=(0, 0))
        content.paste(title, (5, 5), title)
        content.paste(board, ((content.width // 2 - board.width // 2) + 5, Config.PRINT_TITLE_BOX_HEIGHT_PIXELS + 5), board)
        return content

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
                grid.paste(tile_image, ((cell.loc_x * cell_size), (cell.loc_y * cell_size)), tile_image)
        board = Image.new(
            "LA",
            (
                grid.width
                + 2 * (Config.PRINT_GRID_MARGIN_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_PAD_PIXELS),
                grid.height
                + 2 * (Config.PRINT_GRID_MARGIN_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_PAD_PIXELS),
            ),
            color=(0, 0),
        )
        draw = ImageDraw.Draw(board)
        draw.rounded_rectangle(
            [
                (0 + Config.PRINT_GRID_PAD_PIXELS, 0 + Config.PRINT_GRID_PAD_PIXELS),
                (board.width - Config.PRINT_GRID_PAD_PIXELS, board.height - Config.PRINT_GRID_PAD_PIXELS),
            ],
            radius=Config.PRINT_GRID_BORDER_RADIUS_PIXELS,
            fill=(0, 0),
            outline=(0, 255),
            width=Config.PRINT_GRID_BORDER_PIXELS,
        )
        board.paste(grid, (((board.width // 2) - grid.width // 2), ((board.height // 2) - grid.height // 2)), grid)
        if Config.PRINT_DEBUG:
            board = board.convert("RGBA")
            draw = ImageDraw.Draw(board)
            draw.line(
                [(0, Config.PRINT_GRID_PAD_PIXELS), (board.width, Config.PRINT_GRID_PAD_PIXELS)],
                fill=(51, 153, 255, 255),
                width=2,
            )
            draw.line(
                [(0, board.height - Config.PRINT_GRID_PAD_PIXELS), (board.width, board.height - Config.PRINT_GRID_PAD_PIXELS)],
                fill=(51, 153, 255, 255),
                width=2,
            )

            draw.line(
                [
                    (0, Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS),
                    (board.width, Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )
            draw.line(
                [
                    (0, board.height - Config.PRINT_GRID_PAD_PIXELS - Config.PRINT_GRID_BORDER_PIXELS),
                    (board.width, board.height - Config.PRINT_GRID_PAD_PIXELS - Config.PRINT_GRID_BORDER_PIXELS),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )

            draw.line(
                [
                    (0, Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_MARGIN_PIXELS),
                    (
                        board.width,
                        Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )
            draw.line(
                [
                    (
                        0,
                        board.height
                        - Config.PRINT_GRID_PAD_PIXELS
                        - Config.PRINT_GRID_BORDER_PIXELS
                        - Config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                    (
                        board.width,
                        board.height
                        - Config.PRINT_GRID_PAD_PIXELS
                        - Config.PRINT_GRID_BORDER_PIXELS
                        - Config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )

            draw.line(
                [(Config.PRINT_GRID_PAD_PIXELS, 0), (Config.PRINT_GRID_PAD_PIXELS, board.height)],
                fill=(51, 153, 255, 255),
                width=2,
            )
            draw.line(
                [(board.width - Config.PRINT_GRID_PAD_PIXELS, 0), (board.width - Config.PRINT_GRID_PAD_PIXELS, board.height)],
                fill=(51, 153, 255, 255),
                width=2,
            )

            draw.line(
                [
                    (Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS, 0),
                    (Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS, board.height),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )
            draw.line(
                [
                    (board.width - Config.PRINT_GRID_PAD_PIXELS - Config.PRINT_GRID_BORDER_PIXELS, 0),
                    (board.width - Config.PRINT_GRID_PAD_PIXELS - Config.PRINT_GRID_BORDER_PIXELS, board.height),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )

            draw.line(
                [
                    (Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_MARGIN_PIXELS, 0),
                    (
                        Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_MARGIN_PIXELS,
                        board.height,
                    ),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )
            draw.line(
                [
                    (
                        board.width
                        - Config.PRINT_GRID_PAD_PIXELS
                        - Config.PRINT_GRID_BORDER_PIXELS
                        - Config.PRINT_GRID_MARGIN_PIXELS,
                        0,
                    ),
                    (
                        board.width
                        - Config.PRINT_GRID_PAD_PIXELS
                        - Config.PRINT_GRID_BORDER_PIXELS
                        - Config.PRINT_GRID_MARGIN_PIXELS,
                        board.height,
                    ),
                ],
                fill=(51, 153, 255, 255),
                width=2,
            )
            offset = Config.PRINT_GRID_PAD_PIXELS + Config.PRINT_GRID_BORDER_PIXELS + Config.PRINT_GRID_MARGIN_PIXELS
            for n in range(1, self.columns):
                draw.line(
                    [(offset + (n * cell_size), 0), (offset + (n * cell_size), board.height)],
                    fill=(153, 204, 255, 255),
                    width=1,
                )
            for n in range(1, self.rows):
                draw.line(
                    [(0, offset + (n * cell_size)), (board.width, offset + (n * cell_size))],
                    fill=(153, 204, 255, 255),
                    width=1,
                )
        return board

    def check_for_inadvertent_profanity(self):
        grid_strings: dict[str, str] = self._get_grid_strings()
        for name, grid_string in grid_strings.items():
            grid_string_substrings_forward = [
                grid_string[i:j]
                for i in range(len(grid_string))
                for j in range(i + 1, len(grid_string) + 1)
                if grid_string[i:j] in Config.PROFANITY_LIST
            ]
            gird_string_substrings_backward = [
                grid_string[-j:-i:-1]
                for i in range(1, len(grid_string) + 1)
                for j in range(i + 1, len(grid_string) + 2)
                if grid_string[i:j] in Config.PROFANITY_LIST
            ]
            bad_words = grid_string_substrings_forward + gird_string_substrings_backward
            if len(bad_words) > 0:
                Logger.get_logger().warn(f"Profanity found {bad_words}")
                self.profanity[name] = bad_words

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
