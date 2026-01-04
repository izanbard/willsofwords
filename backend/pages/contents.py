from abc import abstractmethod

from PIL import ImageText, ImageDraw, Image, ImageOps

from backend.models import TitlePageEnum, Puzzle, LayoutEnum, BoardImageEnum
from .print_params import PrintParams
from .sub_contents import SubContentsHeader, SubContentsSearchList, SubContentsGrid, SubContentsLongFact


class Contents(PrintParams):
    def __init__(self) -> None:
        super().__init__()
        self.size: tuple[int, int] = (self.config.PRINT_CONTENT_WIDTH_PIXELS, self.config.PRINT_CONTENT_HEIGHT_PIXELS)
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    @abstractmethod
    def get_content_image(self) -> Image.Image:
        raise NotImplementedError


class ContentsFront(Contents):
    def __init__(self, front_type: TitlePageEnum = TitlePageEnum.PUZZLE) -> None:
        super().__init__()
        self.front_type: TitlePageEnum = front_type

    def get_content_image(self) -> Image.Image:
        if self.front_type == TitlePageEnum.PUZZLE:
            words = "A Glorious Front Page Goes Here"
        elif self.front_type == TitlePageEnum.SOLUTION:
            words = "The Solutions you seek are here"
        else:
            raise ValueError("Unknown Board Image Type")
        text: ImageText.Text = ImageText.Text(
            text=words,
            font=self.fonts["TITLE_FONT"],
        )
        self.draw.text(
            xy=(self.base_image.width // 2, self.base_image.height // 2),
            text=text,
            fill=self.colours["SOLID_BLACK"],
            anchor="mm",
            align="centre",
        )

        return self.base_image


class ContentsPuzzleGrid(Contents):
    def __init__(
        self,
        puzzle: Puzzle,
        grid_page_type: LayoutEnum = LayoutEnum.SINGLE,
        grid_image_type: BoardImageEnum = BoardImageEnum.PUZZLE,
    ) -> None:
        super().__init__()
        self.puzzle: Puzzle = puzzle
        self.grid_page_type: LayoutEnum = grid_page_type
        self.grid_image_type: BoardImageEnum = grid_image_type

    def get_content_image(self) -> Image.Image:
        title_image: Image.Image = SubContentsHeader(self.puzzle.display_title).get_content_image()
        grid_image: Image.Image = SubContentsGrid(
            self.puzzle.rows,
            self.puzzle.columns,
            self.puzzle.cells,
            self.puzzle.calculate_cells_size(),
            grid_type=self.grid_image_type,
        ).get_content_image()
        self.base_image.paste(im=title_image, box=(0, 0), mask=title_image)
        self.base_image.paste(
            im=grid_image,
            box=(self.base_image.width // 2 - grid_image.width // 2, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
            mask=grid_image,
        )
        if self.grid_page_type == LayoutEnum.SINGLE and self.grid_image_type == BoardImageEnum.PUZZLE:
            wordlist: Image.Image = SubContentsSearchList(
                self.puzzle.puzzle_search_list, LayoutEnum.SINGLE
            ).get_content_image()
            self.base_image.paste(
                im=wordlist, box=(0, self.base_image.height - self.config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS), mask=wordlist
            )
        if self.config.PRINT_DEBUG:
            self.draw.line(
                [
                    (0, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                    (self.base_image.width, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                ],
                fill=self.colours["DEBUG_GREEN"],
                width=2,
            )
            if self.grid_page_type == LayoutEnum.SINGLE:
                self.draw.line(
                    [
                        (0, self.base_image.height - self.config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS),
                        (self.base_image.width, self.base_image.height - self.config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS),
                    ],
                    fill=self.colours["DEBUG_GREEN"],
                    width=2,
                )
        return self.base_image


class ContentsPuzzleWordlist(Contents):
    def __init__(
        self,
        puzzle: Puzzle,
    ) -> None:
        super().__init__()
        self.puzzle: Puzzle = puzzle

    def get_content_image(self) -> Image.Image:
        title_image: Image.Image = SubContentsHeader(self.puzzle.display_title).get_content_image()
        self.base_image.paste(im=title_image, box=(0, 0), mask=title_image)
        wordlist: Image.Image = SubContentsSearchList(self.puzzle.puzzle_search_list, LayoutEnum.DOUBLE).get_content_image()
        self.base_image.paste(
            im=wordlist,
            box=(self.base_image.width // 2 - wordlist.width // 2, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
            mask=wordlist,
        )
        long_fact: Image.Image = SubContentsLongFact(self.puzzle.long_fact).get_content_image()
        self.base_image.paste(
            long_fact,
            (
                0,
                ((self.base_image.height - self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2)
                + self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS,
            ),
            long_fact,
        )
        if self.config.PRINT_DEBUG:
            self.draw.line(
                [
                    (0, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                    (self.base_image.width, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                ],
                fill=self.colours["DEBUG_GREEN"],
                width=2,
            )

            self.draw.line(
                [
                    (
                        0,
                        ((self.base_image.height - self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2)
                        + self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS,
                    ),
                    (
                        self.base_image.width,
                        ((self.base_image.height - self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2)
                        + self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS,
                    ),
                ],
                fill=self.colours["DEBUG_GREEN"],
                width=2,
            )
        return self.base_image


class ContentsSolution(Contents):
    def __init__(self, puzzle_list: list[Puzzle]) -> None:
        super().__init__()
        self.puzzle_list: list[Puzzle] = puzzle_list

    def _create_solution_tumbnail(self, puzzle: Puzzle) -> Image.Image:
        thumbnail: Image.Image = self._make_base_image()
        title_image: Image.Image = SubContentsHeader(puzzle.display_title).get_content_image()
        thumbnail.paste(im=title_image, box=(0, 0), mask=title_image)
        grid_image: Image.Image = SubContentsGrid(
            puzzle.rows,
            puzzle.columns,
            puzzle.cells,
            puzzle.calculate_cells_size(),
            grid_type=BoardImageEnum.SOLUTION,
        ).get_content_image()
        grid_image = ImageOps.contain(image=grid_image, size=(thumbnail.width, thumbnail.height - title_image.height))
        thumbnail.paste(im=grid_image, box=(0, title_image.height), mask=grid_image)
        return thumbnail

    def get_content_image(self) -> Image.Image:
        col_width = self.config.PRINT_CONTENT_WIDTH_PIXELS // self.config.PRINT_SOLUTION_PAGE_COLS
        row_height = self.config.PRINT_CONTENT_HEIGHT_PIXELS // self.config.PRINT_SOLUTION_PAGE_ROWS
        for n, puzzle in enumerate(self.puzzle_list):
            solution_image: Image.Image = self._create_solution_tumbnail(puzzle)
            solution_thumbnail = ImageOps.contain(image=solution_image, size=(col_width, row_height))
            x = n % self.config.PRINT_SOLUTION_PAGE_COLS
            y = n // self.config.PRINT_SOLUTION_PAGE_COLS
            self.base_image.paste(
                im=solution_thumbnail,
                box=((x * col_width) + (col_width // 2) - (solution_thumbnail.width // 2), y * row_height),
                mask=solution_thumbnail,
            )
        if self.config.PRINT_DEBUG:
            for x in range(1, self.config.PRINT_SOLUTION_PAGE_COLS):
                self.draw.line(
                    xy=[(x * col_width, 0), (x * col_width, self.base_image.height)],
                    fill=self.colours["DEBUG_BLUE"],
                    width=2,
                )
            for y in range(1, self.config.PRINT_SOLUTION_PAGE_ROWS):
                self.draw.line(
                    xy=[(0, y * row_height), (self.base_image.width, y * row_height)],
                    fill=self.colours["DEBUG_BLUE"],
                    width=2,
                )
        return self.base_image


class ContentsBlank(Contents):
    def __init__(self) -> None:
        super().__init__()

    def get_content_image(self) -> Image.Image:
        return self.base_image
