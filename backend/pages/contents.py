from abc import abstractmethod, ABC

from PIL import ImageText, ImageDraw, Image, ImageOps

from backend.models import TitlePageEnum, Puzzle, LayoutEnum, BoardImageEnum, ProjectConfig
from .print_params import PrintParams
from .sub_contents import SubContentsHeader, SubContentsSearchList, SubContentsGrid, SubContentsLongFact
from backend.utils import Logger


class Contents(PrintParams, ABC):
    def __init__(self, *, project_config: ProjectConfig, print_debug: bool = False) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.size: tuple[int, int] = (self.config.content_width_pixels, self.config.content_height_pixels)
        self.base_image: Image.Image = self._make_base_image()
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    @abstractmethod
    def get_content_image(self) -> Image.Image:
        raise NotImplementedError

    def calculate_cells_size(self, columns: int, rows: int) -> int:
        if not self.config.variable_cell_size:
            return self.config.min_cell_size
        cell_size_by_width = self.config.grid_width // columns
        cell_size_by_height = self.config.grid_height // rows
        if cell_size_by_width < self.config.min_cell_size:
            return self.config.min_cell_size
        if cell_size_by_width > self.config.max_cell_size:
            if cell_size_by_height < self.config.min_cell_size:
                return self.config.min_cell_size
            if cell_size_by_height > self.config.max_cell_size:
                return self.config.max_cell_size
            return cell_size_by_height
        if cell_size_by_height < self.config.min_cell_size:
            return cell_size_by_width
        if cell_size_by_height > self.config.max_cell_size:
            return cell_size_by_width
        return min(cell_size_by_height, cell_size_by_width)


class ContentsFront(Contents):
    def __init__(
        self, project_config: ProjectConfig, front_type: TitlePageEnum = TitlePageEnum.PUZZLE, print_debug: bool = False
    ) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.front_type: TitlePageEnum = front_type

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for {self.front_type}")
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
        project_config: ProjectConfig,
        grid_page_type: LayoutEnum = LayoutEnum.SINGLE,
        grid_image_type: BoardImageEnum = BoardImageEnum.PUZZLE,
        print_debug: bool = False,
    ) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.puzzle: Puzzle = puzzle
        self.grid_page_type: LayoutEnum = grid_page_type
        self.grid_image_type: BoardImageEnum = grid_image_type

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(
            f"Generating {self.__class__} image for puzzle grid of {self.puzzle.display_title} with layout {self.grid_page_type}"
        )
        title_image: Image.Image = SubContentsHeader(
            header_title=self.puzzle.display_title, project_config=self.config, print_debug=self.print_debug
        ).get_content_image()
        cell_size = self.calculate_cells_size(self.puzzle.columns, self.puzzle.rows)
        grid_image: Image.Image = SubContentsGrid(
            rows=self.puzzle.rows,
            cols=self.puzzle.columns,
            cells=self.puzzle.cells,
            cell_size=cell_size,
            grid_type=self.grid_image_type,
            project_config=self.config,
            print_debug=self.print_debug,
        ).get_content_image()
        self.base_image.paste(im=title_image, box=(0, 0), mask=title_image)
        self.base_image.paste(
            im=grid_image,
            box=(self.base_image.width // 2 - grid_image.width // 2, self.config.title_box_height_pixels),
            mask=grid_image,
        )
        if self.grid_page_type == LayoutEnum.SINGLE and self.grid_image_type == BoardImageEnum.PUZZLE:
            wordlist: Image.Image = SubContentsSearchList(
                wordlist=self.puzzle.puzzle_search_list,
                layout_type=LayoutEnum.SINGLE,
                project_config=self.config,
                print_debug=self.print_debug,
            ).get_content_image()
            self.base_image.paste(
                im=wordlist, box=(0, self.base_image.height - self.config.wordlist_box_height_pixels), mask=wordlist
            )
        if self.print_debug:
            self.draw.line(
                [
                    (0, self.config.title_box_height_pixels),
                    (self.base_image.width, self.config.title_box_height_pixels),
                ],
                fill=self.colours["DEBUG_GREEN"],
                width=2,
            )
            if self.grid_page_type == LayoutEnum.SINGLE:
                self.draw.line(
                    [
                        (0, self.base_image.height - self.config.wordlist_box_height_pixels),
                        (self.base_image.width, self.base_image.height - self.config.wordlist_box_height_pixels),
                    ],
                    fill=self.colours["DEBUG_GREEN"],
                    width=2,
                )
            debug_text = ImageText.Text(
                text=f"Grid Size: {self.puzzle.columns}x{self.puzzle.rows}\n"
                f"Density: {self.puzzle.density:.2%}\n"
                f"Cell Size: {cell_size}px, {cell_size / self.config.dpi:.3f}in\n",
                font=self.fonts["CELL_DEBUG_FONT"],
            )
            self.draw.text(xy=(10, 10), text=debug_text, fill=self.colours["DEBUG_BLUE"], anchor="la", align="left")
            self.draw.rectangle(
                xy=[(7, 9), (debug_text.get_bbox()[2] + 13, debug_text.get_bbox()[3] + 13)],
                outline=self.colours["DEBUG_BLUE"],
                width=2,
            )
        return self.base_image


class ContentsPuzzleWordlist(Contents):
    def __init__(self, puzzle: Puzzle, project_config: ProjectConfig, print_debug: bool = False) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.puzzle: Puzzle = puzzle

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for puzzle wordlist for {self.puzzle.display_title}")
        title_image: Image.Image = SubContentsHeader(
            header_title=self.puzzle.display_title, project_config=self.config, print_debug=self.print_debug
        ).get_content_image()
        self.base_image.paste(im=title_image, box=(0, 0), mask=title_image)
        wordlist: Image.Image = SubContentsSearchList(
            wordlist=self.puzzle.puzzle_search_list,
            layout_type=LayoutEnum.DOUBLE,
            project_config=self.config,
            print_debug=self.print_debug,
        ).get_content_image()
        self.base_image.paste(
            im=wordlist,
            box=(self.base_image.width // 2 - wordlist.width // 2, self.config.title_box_height_pixels),
            mask=wordlist,
        )
        long_fact: Image.Image = SubContentsLongFact(
            long_fact=self.puzzle.long_fact, project_config=self.config, print_debug=self.print_debug
        ).get_content_image()
        self.base_image.paste(
            long_fact,
            (
                0,
                ((self.base_image.height - self.config.title_box_height_pixels) // 2) + self.config.title_box_height_pixels,
            ),
            long_fact,
        )
        if self.print_debug:
            self.draw.line(
                [
                    (0, self.config.title_box_height_pixels),
                    (self.base_image.width, self.config.title_box_height_pixels),
                ],
                fill=self.colours["DEBUG_GREEN"],
                width=2,
            )

            self.draw.line(
                [
                    (
                        0,
                        ((self.base_image.height - self.config.title_box_height_pixels) // 2)
                        + self.config.title_box_height_pixels,
                    ),
                    (
                        self.base_image.width,
                        ((self.base_image.height - self.config.title_box_height_pixels) // 2)
                        + self.config.title_box_height_pixels,
                    ),
                ],
                fill=self.colours["DEBUG_GREEN"],
                width=2,
            )
        return self.base_image


class ContentsSolution(Contents):
    def __init__(self, puzzle_list: list[Puzzle], project_config: ProjectConfig, print_debug: bool = False) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.puzzle_list: list[Puzzle] = puzzle_list

    def _create_solution_thumbnail(self, puzzle: Puzzle) -> Image.Image:
        thumbnail: Image.Image = self._make_base_image()
        title_image: Image.Image = SubContentsHeader(
            header_title=puzzle.display_title, project_config=self.config, print_debug=self.print_debug
        ).get_content_image()
        thumbnail.paste(im=title_image, box=(0, 0), mask=title_image)
        grid_image: Image.Image = SubContentsGrid(
            rows=puzzle.rows,
            cols=puzzle.columns,
            cells=puzzle.cells,
            cell_size=self.calculate_cells_size(puzzle.columns, puzzle.rows),
            grid_type=BoardImageEnum.SOLUTION,
            project_config=self.config,
            print_debug=self.print_debug,
        ).get_content_image()
        grid_image = ImageOps.contain(image=grid_image, size=(thumbnail.width, thumbnail.height - title_image.height))
        thumbnail.paste(im=grid_image, box=(0, title_image.height), mask=grid_image)
        return thumbnail

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for puzzle solution with {len(self.puzzle_list)}")
        col_width = self.config.content_width_pixels // self.config.solution_page_cols
        row_height = self.config.content_height_pixels // self.config.solution_page_rows
        for n, puzzle in enumerate(self.puzzle_list):
            solution_image: Image.Image = self._create_solution_thumbnail(puzzle)
            solution_thumbnail = ImageOps.contain(image=solution_image, size=(col_width, row_height))
            x = n % self.config.solution_page_cols
            y = n // self.config.solution_page_cols
            self.base_image.paste(
                im=solution_thumbnail,
                box=((x * col_width) + (col_width // 2) - (solution_thumbnail.width // 2), y * row_height),
                mask=solution_thumbnail,
            )
        if self.print_debug:
            for x in range(1, self.config.solution_page_cols):
                self.draw.line(
                    xy=[(x * col_width, 0), (x * col_width, self.base_image.height)],
                    fill=self.colours["DEBUG_BLUE"],
                    width=2,
                )
            for y in range(1, self.config.solution_page_rows):
                self.draw.line(
                    xy=[(0, y * row_height), (self.base_image.width, y * row_height)],
                    fill=self.colours["DEBUG_BLUE"],
                    width=2,
                )
        return self.base_image


class ContentsBlank(Contents):
    def __init__(self, project_config: ProjectConfig, print_debug: bool = False) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)

    def get_content_image(self) -> Image.Image:
        Logger.get_logger().debug(f"Generating {self.__class__} image for blank page")
        return self.base_image
