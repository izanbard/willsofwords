from abc import abstractmethod
from copy import copy
from math import ceil

from PIL import ImageDraw, ImageText, Image


from src.models import Cell, LayoutEnum, BoardImageEnum, DirectionEnum
from .print_params import PrintParams


class SubContents(PrintParams):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_content_image(self) -> Image.Image:
        raise NotImplementedError


class SubContentsHeader(SubContents):
    def __init__(self, header_title: str) -> None:
        super().__init__()
        self.size: tuple[int, int] = (self.config.PRINT_CONTENT_WIDTH_PIXELS, self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS)
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.header_title: str = header_title

    def get_content_image(self) -> Image.Image:
        text: ImageText.Text = ImageText.Text(text=self.header_title, font=self.fonts["TITLE_FONT"])
        self.draw.text(
            xy=(self.base_image.width // 2, self.base_image.height // 2),
            text=text,
            fill=self.colours["SOLID_BLACK"],
            anchor="mm",
        )
        return self.base_image


class SubContentsSearchList(SubContents):
    def __init__(self, wordlist: list[str], layout_type: LayoutEnum = LayoutEnum.SINGLE) -> None:
        super().__init__()
        if layout_type == layout_type.SINGLE:
            self.size: tuple[int, int] = (self.config.PRINT_CONTENT_WIDTH_PIXELS, self.config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS)
        else:
            self.size: tuple[int, int] = (
                self.config.PRINT_CONTENT_WIDTH_PIXELS,
                (self.config.PRINT_CONTENT_HEIGHT_PIXELS - self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2,
            )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.wordlist: list[str] = wordlist
        self.layout_type: LayoutEnum = layout_type

    def get_content_image(self) -> Image.Image:
        column_width, columns = self._calculate_font_size()

        for column_number in range(len(columns)):
            self.draw.text(
                xy=(int(column_number * column_width) + (column_width // 2), 0),
                text=columns[column_number],
                align="left",
                anchor="ma",
                fill=self.colours["SOLID_BLACK"],
            )
        if self.config.PRINT_DEBUG:
            for column_number in range(1, len(columns)):
                self.draw.line(
                    xy=[
                        (int(column_number * column_width), 0),
                        (int(column_number * column_width), self.base_image.height),
                    ],
                    fill=self.colours["DEBUG_BLUE"],
                    width=2,
                )
        return self.base_image

    def _calculate_font_size(self) -> tuple[int, list[ImageText.Text]]:
        number_of_words = len(self.wordlist)
        column_width = self.config.PRINT_CONTENT_WIDTH_PIXELS // 3
        columns: list[ImageText.Text] = []
        font = copy(self.fonts["SEARCH_LIST_FONT"])
        exceeds_size = True
        while exceeds_size:
            font = font.font_variant(size=font.size - 1)
            if font.size <= 0:
                raise ValueError("wordlist font too small")
            dummy_text = ImageText.Text(text=self.wordlist[0], font=font)
            line_height = int(dummy_text.get_bbox()[3]) + self.config.PRINT_WORDLIST_LINE_SPACING_PIXELS

            max_sublist_length = int(self.base_image.height / line_height)
            number_of_columns = max(ceil(number_of_words / max_sublist_length), 3)

            chunk_size = ceil(number_of_words / number_of_columns)
            column_width = self.config.PRINT_CONTENT_WIDTH_PIXELS // number_of_columns

            columns: list[ImageText.Text] = []
            for column_number in range(number_of_columns):
                text = ImageText.Text(
                    text="\n".join(self.wordlist[column_number * chunk_size : (column_number * chunk_size) + chunk_size]),
                    font=font,
                    spacing=self.config.PRINT_WORDLIST_LINE_SPACING_PIXELS,
                )
                columns.append(text)
            exceeds_size = any(x.get_bbox()[2] > column_width for x in columns)
        return column_width, columns


class SubContentsCell(SubContents):
    def __init__(self, cell: Cell, cell_size: int, grid_type: BoardImageEnum = BoardImageEnum.PUZZLE):
        super().__init__()
        self.cell: Cell = cell
        self.solution_line_width = int(cell_size / 10)
        if grid_type == BoardImageEnum.PUZZLE:
            self.size: tuple[int, int] = (cell_size, cell_size)
        else:
            self.size: tuple[int, int] = (
                cell_size + ceil(self.solution_line_width / 2 * (2**0.5)),
                cell_size + ceil(self.solution_line_width / 2 * (2**0.5)),
            )
        self.grid_type: BoardImageEnum = grid_type
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    def get_content_image(self) -> Image.Image:
        text: ImageText.Text = ImageText.Text(text=self.cell.value, font=self.fonts["CELL_FONT"])

        self.draw.text(
            xy=(self.base_image.width // 2, self.base_image.height // 2),
            text=text,
            fill=self.colours["SOLID_BLACK"],
            anchor="mm",
        )
        if self.grid_type == BoardImageEnum.SOLUTION:
            if self.cell.direction[DirectionEnum.NS]:
                self.draw.line(
                    xy=((self.base_image.width // 2, 0), (self.base_image.width / 2, self.base_image.height)),
                    fill=self.colours["SOLID_BLACK"],
                    width=self.solution_line_width,
                )
            if self.cell.direction[DirectionEnum.EW]:
                self.draw.line(
                    ((0, self.base_image.height / 2), (self.base_image.width, self.base_image.height / 2)),
                    fill=self.colours["SOLID_BLACK"],
                    width=self.solution_line_width,
                )
            if self.cell.direction[DirectionEnum.NESW]:
                self.draw.line(
                    ((0, self.base_image.height), (self.base_image.width, 0)),
                    fill=self.colours["SOLID_BLACK"],
                    width=self.solution_line_width,
                )
            if self.cell.direction[DirectionEnum.NWSE]:
                self.draw.line(
                    ((0, 0), (self.base_image.width, self.base_image.height)),
                    fill=self.colours["SOLID_BLACK"],
                    width=self.solution_line_width,
                )
        return self.base_image


class SubContentsGrid(SubContents):
    def __init__(
        self, rows: int, cols: int, cells: list[list[Cell]], cell_size: int, grid_type: BoardImageEnum = BoardImageEnum.PUZZLE
    ) -> None:
        super().__init__()
        self.rows: int = rows
        self.cols: int = cols
        self.cells: list[list[Cell]] = cells
        self.cell_size = cell_size
        self.grid_type: BoardImageEnum = grid_type
        self.offset = (
            self.config.PRINT_GRID_PAD_PIXELS + self.config.PRINT_GRID_BORDER_PIXELS + self.config.PRINT_GRID_MARGIN_PIXELS
        )
        self.size: tuple[int, int] = (
            self.cols * self.cell_size + 2 * self.offset,
            self.rows * self.cell_size + 2 * self.offset,
        )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    def get_content_image(self) -> Image.Image:
        for row in self.cells:
            for cell in row:
                tile_image = SubContentsCell(cell, self.cell_size, self.grid_type).get_content_image()
                if self.grid_type == BoardImageEnum.PUZZLE:
                    box = ((cell.loc_x * self.cell_size) + self.offset, (cell.loc_y * self.cell_size) + self.offset)
                else:
                    solution_offset = ceil(int(self.cell_size / 10) / 2 * (2**0.5))
                    box = (
                        (cell.loc_x * self.cell_size) + self.offset - solution_offset,
                        (cell.loc_y * self.cell_size) + self.offset - solution_offset,
                    )
                self.base_image.paste(
                    im=tile_image,
                    box=box,
                    mask=tile_image,
                )

        self.draw.rounded_rectangle(
            [
                (self.config.PRINT_GRID_PAD_PIXELS, self.config.PRINT_GRID_PAD_PIXELS),
                (
                    self.base_image.width - self.config.PRINT_GRID_PAD_PIXELS,
                    self.base_image.height - self.config.PRINT_GRID_PAD_PIXELS,
                ),
            ],
            radius=self.config.PRINT_GRID_BORDER_RADIUS_PIXELS,
            fill=None,
            outline=self.colours["SOLID_BLACK"],
            width=self.config.PRINT_GRID_BORDER_PIXELS,
        )
        if self.config.PRINT_DEBUG:
            self.draw.line(
                [(0, self.config.PRINT_GRID_PAD_PIXELS), (self.base_image.width - 1, self.config.PRINT_GRID_PAD_PIXELS)],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (0, self.base_image.height - self.config.PRINT_GRID_PAD_PIXELS - 1),
                    (self.base_image.width - 1, self.base_image.height - self.config.PRINT_GRID_PAD_PIXELS - 1),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (0, self.config.PRINT_GRID_PAD_PIXELS + self.config.PRINT_GRID_BORDER_PIXELS),
                    (self.base_image.width - 1, self.config.PRINT_GRID_PAD_PIXELS + self.config.PRINT_GRID_BORDER_PIXELS),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (0, self.base_image.height - self.config.PRINT_GRID_PAD_PIXELS - self.config.PRINT_GRID_BORDER_PIXELS - 1),
                    (
                        self.base_image.width - 1,
                        self.base_image.height - self.config.PRINT_GRID_PAD_PIXELS - self.config.PRINT_GRID_BORDER_PIXELS - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (
                        0,
                        self.config.PRINT_GRID_PAD_PIXELS
                        + self.config.PRINT_GRID_BORDER_PIXELS
                        + self.config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                    (
                        self.base_image.width - 1,
                        self.config.PRINT_GRID_PAD_PIXELS
                        + self.config.PRINT_GRID_BORDER_PIXELS
                        + self.config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (
                        0,
                        self.base_image.height
                        - 1
                        - self.config.PRINT_GRID_PAD_PIXELS
                        - self.config.PRINT_GRID_BORDER_PIXELS
                        - self.config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                    (
                        self.base_image.width - 1,
                        self.base_image.height
                        - 1
                        - self.config.PRINT_GRID_PAD_PIXELS
                        - self.config.PRINT_GRID_BORDER_PIXELS
                        - self.config.PRINT_GRID_MARGIN_PIXELS,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [(self.config.PRINT_GRID_PAD_PIXELS, 0), (self.config.PRINT_GRID_PAD_PIXELS, self.base_image.height - 1)],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (self.base_image.width - self.config.PRINT_GRID_PAD_PIXELS - 1, 0),
                    (self.base_image.width - self.config.PRINT_GRID_PAD_PIXELS - 1, self.base_image.height - 1),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (self.config.PRINT_GRID_PAD_PIXELS + self.config.PRINT_GRID_BORDER_PIXELS, 0),
                    (self.config.PRINT_GRID_PAD_PIXELS + self.config.PRINT_GRID_BORDER_PIXELS, self.base_image.height - 1),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (self.base_image.width - self.config.PRINT_GRID_PAD_PIXELS - self.config.PRINT_GRID_BORDER_PIXELS - 1, 0),
                    (
                        self.base_image.width - self.config.PRINT_GRID_PAD_PIXELS - self.config.PRINT_GRID_BORDER_PIXELS - 1,
                        self.base_image.height - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (
                        self.config.PRINT_GRID_PAD_PIXELS
                        + self.config.PRINT_GRID_BORDER_PIXELS
                        + self.config.PRINT_GRID_MARGIN_PIXELS,
                        0,
                    ),
                    (
                        self.config.PRINT_GRID_PAD_PIXELS
                        + self.config.PRINT_GRID_BORDER_PIXELS
                        + self.config.PRINT_GRID_MARGIN_PIXELS,
                        self.base_image.height - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (
                        self.base_image.width
                        - 1
                        - self.config.PRINT_GRID_PAD_PIXELS
                        - self.config.PRINT_GRID_BORDER_PIXELS
                        - self.config.PRINT_GRID_MARGIN_PIXELS,
                        0,
                    ),
                    (
                        self.base_image.width
                        - 1
                        - self.config.PRINT_GRID_PAD_PIXELS
                        - self.config.PRINT_GRID_BORDER_PIXELS
                        - self.config.PRINT_GRID_MARGIN_PIXELS,
                        self.base_image.height - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            for n in range(1, self.cols):
                self.draw.line(
                    [(self.offset + (n * self.cell_size), 0), (self.offset + (n * self.cell_size), self.base_image.height)],
                    fill=(153, 204, 255, 255),
                    width=1,
                )
            for n in range(1, self.rows):
                self.draw.line(
                    [(0, self.offset + (n * self.cell_size)), (self.base_image.width, self.offset + (n * self.cell_size))],
                    fill=(153, 204, 255, 255),
                    width=1,
                )

        return self.base_image


class SubContentsLongFact(SubContents):
    def __init__(self, long_fact: str):
        super().__init__()
        self.size: tuple[int, int] = (
            self.config.PRINT_CONTENT_WIDTH_PIXELS,
            (self.config.PRINT_CONTENT_HEIGHT_PIXELS - self.config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2,
        )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.long_fact = long_fact

    def get_content_image(self) -> Image.Image:
        title: ImageText.Text = ImageText.Text(text="Did you know?", font=self.fonts["HEADING_FONT"])
        self.draw.text(
            xy=(0, 0),
            text=title,
            fill=self.colours["SOLID_BLACK"],
        )
        paragraph: ImageText.Text = self._get_paragraph(self.long_fact)
        self.draw.text(
            xy=(0, title.get_bbox()[3]),
            text=paragraph,
            fill=self.colours["SOLID_BLACK"],
            align="left",
            spacing=self.config.PRINT_LONG_FACT_LINE_SPACING_PIXELS,
        )
        return self.base_image

    def _get_paragraph(self, long_fact: str) -> ImageText.Text:
        split_list = []
        temp_list = []
        for word in long_fact.split():
            line = ImageText.Text(
                text=" ".join(temp_list + [word]),
                font=self.fonts["CONTENT_FONT"],
            )
            if line.get_length() < self.config.PRINT_CONTENT_WIDTH_PIXELS:
                temp_list.append(word)
            else:
                split_list.append(temp_list)
                temp_list = [word]
        paragraph = ImageText.Text(
            "\n".join([" ".join(x) for x in split_list]),
            font=self.fonts["CONTENT_FONT"],
        )
        return paragraph


class SubContentsPageNumber(SubContents):
    def __init__(self, page_number: str):
        super().__init__()
        self.size: tuple[int, int] = (
            self.config.PRINT_PAGE_NUMBER_FONT_SIZE_PIXELS + self.config.PRINT_PAGE_NUMBER_OFFSET_PIXELS,
            self.config.PRINT_PAGE_NUMBER_FONT_SIZE_PIXELS + self.config.PRINT_PAGE_NUMBER_OFFSET_PIXELS,
        )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.page_number = page_number

    def get_content_image(self) -> Image.Image:
        text = ImageText.Text(text=self.page_number, font=self.fonts["PAGE_NUMBER_FONT"])
        self.draw.text(
            xy=(self.base_image.width // 2, self.base_image.height // 2),
            text=text,
            anchor="mm",
            fill=self.colours["SOLID_BLACK"],
        )
        if self.config.PRINT_DEBUG:
            self.draw.rectangle(
                xy=[(0, 0), (self.base_image.width - 1, self.base_image.height - 1)],
                fill=None,
                outline=self.colours["DEBUG_BLUE"],
                width=1,
            )
        return self.base_image
