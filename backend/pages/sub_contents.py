from abc import ABC, abstractmethod
from copy import copy
from math import ceil

from PIL import Image, ImageDraw, ImageText

from backend.models import (
    BoardImageEnum,
    Cell,
    DirectionEnum,
    LayoutEnum,
    ProjectConfig,
)
from backend.utils import Logger

from .print_params import PrintParams


class SubContents(PrintParams, ABC):
    ROOT_TWO_APPX = 1.42

    def __init__(self, *, project_config: ProjectConfig, print_debug: bool = False) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)

    @abstractmethod
    def get_content_image(self) -> Image.Image:
        raise NotImplementedError


class SubContentsHeader(SubContents):
    def __init__(self, header_title: str, project_config: ProjectConfig, print_debug: bool = False) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.size: tuple[int, int] = (self.config.content_width_pixels, self.config.title_box_height_pixels)
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.header_title: str = header_title

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for header {self.header_title}")
        text: ImageText.Text = ImageText.Text(text=self.header_title, font=self.fonts["TITLE_FONT"])
        self.draw.text(
            xy=(self.base_image.width // 2, self.base_image.height // 2),
            text=text,
            fill=self.colours["SOLID_BLACK"],
            anchor="mm",
        )
        return self.base_image


class SubContentsSearchList(SubContents):
    def __init__(
        self,
        wordlist: list[str],
        project_config: ProjectConfig,
        layout_type: LayoutEnum = LayoutEnum.SINGLE,
        print_debug: bool = False,
    ) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        if layout_type == layout_type.SINGLE:
            self.size: tuple[int, int] = (self.config.content_width_pixels, self.config.wordlist_box_height_pixels)
        else:
            self.size: tuple[int, int] = (
                self.config.content_width_pixels,
                (self.config.content_height_pixels - self.config.title_box_height_pixels) // 2,
            )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.wordlist: list[str] = wordlist
        self.layout_type: LayoutEnum = layout_type

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(
            f"Generating {self.__class__} image for search list with {len(self.wordlist)} words, layout {self.layout_type}"
        )
        column_width, columns = self._calculate_font_size()

        for column_number in range(len(columns)):
            self.draw.text(
                xy=(int(column_number * column_width) + (column_width // 2), 0),
                text=columns[column_number],
                align="left",
                anchor="ma",
                fill=self.colours["SOLID_BLACK"],
            )
        if self.print_debug:
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
        column_width = self.config.content_width_pixels // 3
        columns: list[ImageText.Text] = []
        font = copy(self.fonts["SEARCH_LIST_FONT"])
        exceeds_size = True
        while exceeds_size:
            font = font.font_variant(size=font.size - 1)
            if font.size <= 0:
                raise ValueError("wordlist font too small")
            dummy_text = ImageText.Text(text=self.wordlist[0], font=font)
            line_height = int(dummy_text.get_bbox()[3]) + self.config.wordlist_line_spacing_pixels

            max_sublist_length = int(self.base_image.height / line_height)
            number_of_columns = max(ceil(number_of_words / max_sublist_length), 3)

            chunk_size = ceil(number_of_words / number_of_columns)
            column_width = self.config.content_width_pixels // number_of_columns

            columns: list[ImageText.Text] = []
            for column_number in range(number_of_columns):
                text = ImageText.Text(
                    text="\n".join(self.wordlist[column_number * chunk_size : (column_number * chunk_size) + chunk_size]),
                    font=font,
                    spacing=self.config.wordlist_line_spacing_pixels,
                )
                columns.append(text)
            exceeds_size = any(x.get_bbox()[2] > column_width for x in columns)
        return column_width, columns


class SubContentsCell(SubContents):
    """
    Representation of a subcontent cell with additional rendering capabilities.

    The SubContentsCell class extends the functionality of the SubContents class
    to create a visual representation of a cell, with options for rendering
    specific grid types (e.g. puzzle or solution grids). It prepares a base image
    and provides methods to add rendered content to it, taking into account
    directions and visual styles specific to the grid type.

    :ivar cell: The cell object containing information about the cell, such as its
        value and directional properties.
    :type cell: Cell
    :ivar solution_line_width: The width of the lines used to represent directional
        paths in the solution grid.
    :type solution_line_width: int
    :ivar size: The dimensions of the cell. This depends on the specified grid
        type and cell size.
    :type size: tuple[int, int]
    :ivar grid_type: The type of grid (e.g. puzzle or solution) to render for
        the cell.
    :type grid_type: BoardImageEnum
    :ivar base_image: The base image on which the cell and its contents are drawn.
    :type base_image: Image.Image
    :ivar draw: The drawing object used to render visuals on the base image.
    :type draw: ImageDraw.ImageDraw
    """

    def __init__(
        self,
        cell: Cell,
        cell_size: int,
        project_config: ProjectConfig,
        grid_type: BoardImageEnum = BoardImageEnum.PUZZLE,
        print_debug: bool = False,
    ):
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.cell: Cell = cell
        self.solution_line_width = int(cell_size / 10)
        if grid_type == BoardImageEnum.PUZZLE:
            self.size: tuple[int, int] = (cell_size, cell_size)
        else:
            self.size: tuple[int, int] = (
                cell_size + ceil(self.solution_line_width / 2 * self.ROOT_TWO_APPX),
                cell_size + ceil(self.solution_line_width / 2 * self.ROOT_TWO_APPX),
            )
        self.grid_type: BoardImageEnum = grid_type
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    def get_content_image(self) -> Image.Image:
        """
        Generates and returns a content image with text and optional grid or line decorations based
        on the cell's current state and grid type.

        The method renders the text from the specified cell and font onto the base image
        and optionally draws directional lines based on the cell's directional properties.
        Directional lines are added if the `grid_type` matches the solution board type and
        the corresponding directions are enabled.

        :raises KeyError: If a required key is missing in the `fonts` or `colours` dictionaries, or
                          the necessary directions are not present in the cell's directional properties.

        :return: An `Image.Image` object that contains the rendered content.
        :rtype: PIL.Image.Image
        """
        Logger.get_logger().debug(
            f"Generating {self.__class__} image for cell ({self.cell.loc_x},{self.cell.loc_y}) with value {self.cell.value} and grid type {self.grid_type}"
        )
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
        self,
        rows: int,
        cols: int,
        cells: list[list[Cell]],
        cell_size: int,
        project_config: ProjectConfig,
        grid_type: BoardImageEnum = BoardImageEnum.PUZZLE,
        print_debug: bool = False,
    ) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.rows: int = rows
        self.cols: int = cols
        self.cells: list[list[Cell]] = cells
        self.cell_size = cell_size
        self.grid_type: BoardImageEnum = grid_type
        self.offset = self.config.grid_pad_pixels + self.config.grid_border_pixels + self.config.grid_margin_pixels
        self.size: tuple[int, int] = (
            self.cols * self.cell_size + 2 * self.offset,
            self.rows * self.cell_size + 2 * self.offset,
        )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(
            f"Generating {self.__class__} image for grid with {self.rows} rows, {self.cols} columns and grid type {self.grid_type}"
        )
        for row in self.cells:
            for cell in row:
                tile_image = SubContentsCell(
                    cell=cell,
                    cell_size=self.cell_size,
                    grid_type=self.grid_type,
                    project_config=self.config,
                    print_debug=self.print_debug,
                ).get_content_image()
                if self.grid_type == BoardImageEnum.PUZZLE:
                    box = ((cell.loc_x * self.cell_size) + self.offset, (cell.loc_y * self.cell_size) + self.offset)
                else:
                    solution_offset = ceil(int(self.cell_size / 10) / 2 * self.ROOT_TWO_APPX)
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
                (self.config.grid_pad_pixels, self.config.grid_pad_pixels),
                (
                    self.base_image.width - self.config.grid_pad_pixels,
                    self.base_image.height - self.config.grid_pad_pixels,
                ),
            ],
            radius=self.config.grid_border_radius_pixels,
            fill=None,
            outline=self.colours["SOLID_BLACK"],
            width=self.config.grid_border_pixels,
        )
        if self.print_debug:
            for r in range(self.rows):
                char = ImageText.Text(text=str(r), font=self.fonts["CELL_DEBUG_FONT"])
                self.draw.text(
                    text=char,
                    fill=self.colours["DEBUG_BLUE"],
                    xy=(self.offset // 2, self.offset + self.cell_size // 2 + (r * self.cell_size)),
                    anchor="mm",
                )
            for c in range(self.cols):
                char = ImageText.Text(text=str(c), font=self.fonts["CELL_DEBUG_FONT"])
                self.draw.text(
                    text=char,
                    fill=self.colours["DEBUG_BLUE"],
                    xy=(self.offset + self.cell_size // 2 + (c * self.cell_size), self.offset // 2),
                    anchor="mm",
                )

            self.draw.line(
                [(0, self.config.grid_pad_pixels), (self.base_image.width - 1, self.config.grid_pad_pixels)],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (0, self.base_image.height - self.config.grid_pad_pixels - 1),
                    (self.base_image.width - 1, self.base_image.height - self.config.grid_pad_pixels - 1),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (0, self.config.grid_pad_pixels + self.config.grid_border_pixels),
                    (self.base_image.width - 1, self.config.grid_pad_pixels + self.config.grid_border_pixels),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (0, self.base_image.height - self.config.grid_pad_pixels - self.config.grid_border_pixels - 1),
                    (
                        self.base_image.width - 1,
                        self.base_image.height - self.config.grid_pad_pixels - self.config.grid_border_pixels - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (
                        0,
                        self.offset,
                    ),
                    (
                        self.base_image.width - 1,
                        self.offset,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (
                        0,
                        self.base_image.height - 1 - self.offset,
                    ),
                    (
                        self.base_image.width - 1,
                        self.base_image.height - 1 - self.offset,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [(self.config.grid_pad_pixels, 0), (self.config.grid_pad_pixels, self.base_image.height - 1)],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (self.base_image.width - self.config.grid_pad_pixels - 1, 0),
                    (self.base_image.width - self.config.grid_pad_pixels - 1, self.base_image.height - 1),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (self.config.grid_pad_pixels + self.config.grid_border_pixels, 0),
                    (self.config.grid_pad_pixels + self.config.grid_border_pixels, self.base_image.height - 1),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (self.base_image.width - self.config.grid_pad_pixels - self.config.grid_border_pixels - 1, 0),
                    (
                        self.base_image.width - self.config.grid_pad_pixels - self.config.grid_border_pixels - 1,
                        self.base_image.height - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )

            self.draw.line(
                [
                    (
                        self.offset,
                        0,
                    ),
                    (
                        self.offset,
                        self.base_image.height - 1,
                    ),
                ],
                fill=self.colours["DEBUG_BLUE"],
                width=2,
            )
            self.draw.line(
                [
                    (
                        self.base_image.width - 1 - self.offset,
                        0,
                    ),
                    (
                        self.base_image.width - 1 - self.offset,
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
    def __init__(self, long_fact: str, project_config: ProjectConfig, print_debug: bool = False):
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.size: tuple[int, int] = (
            self.config.content_width_pixels,
            (self.config.content_height_pixels - self.config.title_box_height_pixels) // 2,
        )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.long_fact = long_fact

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for long fact: {self.long_fact[:50]}")
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
            spacing=self.config.long_fact_line_spacing_pixels,
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
            if line.get_length() < self.config.content_width_pixels:
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
    def __init__(self, page_number: str, project_config: ProjectConfig, print_debug: bool = False):
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.size: tuple[int, int] = (
            self.config.page_number_font_size_pixels + self.config.page_number_offset_pixels,
            self.config.page_number_font_size_pixels + self.config.page_number_offset_pixels,
        )
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)
        self.page_number = page_number

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for page number: {self.page_number}")
        text = ImageText.Text(text=self.page_number, font=self.fonts["PAGE_NUMBER_FONT"])
        self.draw.text(
            xy=(self.base_image.width // 2, self.base_image.height // 2),
            text=text,
            anchor="mm",
            fill=self.colours["SOLID_BLACK"],
        )
        if self.print_debug:
            self.draw.rectangle(
                xy=[(0, 0), (self.base_image.width - 1, self.base_image.height - 1)],
                fill=None,
                outline=self.colours["DEBUG_BLUE"],
                width=1,
            )
        return self.base_image
