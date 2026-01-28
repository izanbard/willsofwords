from pathlib import Path as FilePath

from PIL import Image, ImageDraw

from backend.models import (
    LayoutEnum,
    PageTypeEnum,
    ProjectConfig,
    PuzzleData,
)
from backend.utils import Logger, clear_marker_file, set_marker_file

from .contents import (
    ContentsBlank,
    ContentsFront,
    ContentsPuzzleGrid,
    ContentsPuzzleWordlist,
    ContentsSolution,
)
from .print_params import PrintParams
from .sub_contents import SubContentsPageNumber


class Page(PrintParams):
    def __init__(
        self, content: Image.Image, page_number: int, project_config: ProjectConfig, print_debug: bool = False
    ) -> None:
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.content: Image.Image = content
        self.page_number: int = page_number
        self.page_type: PageTypeEnum = PageTypeEnum.RECTO if self.page_number % 2 == 1 else PageTypeEnum.VERSO
        self.size = (self.config.page_width_pixels, self.config.page_height_pixels)
        self.base_image: Image.Image = self._make_base_image("SOLID_WHITE")
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    def get_page_image(self) -> Image.Image:
        if self.page_type == PageTypeEnum.VERSO:
            left_margin_x_coord = self.config.outer_margin_pixels
            right_margin_x_coord = self.config.page_width_pixels - self.config.inner_margin_pixels
        else:
            left_margin_x_coord = self.config.inner_margin_pixels
            right_margin_x_coord = self.config.page_width_pixels - self.config.outer_margin_pixels
        y_coord = self.config.top_margin_pixels
        self.base_image.paste(im=self.content, box=(left_margin_x_coord, y_coord), mask=self.content)
        if self.page_number > 1:
            page_number_image = SubContentsPageNumber(
                page_number=str(self.page_number), project_config=self.config, print_debug=self.print_debug
            ).get_content_image()
            if self.page_type == PageTypeEnum.RECTO:
                page_number_location = (
                    right_margin_x_coord - page_number_image.width,
                    self.config.page_height_pixels - self.config.bottom_margin_pixels - page_number_image.height,
                )
            else:
                page_number_location = (
                    left_margin_x_coord,
                    self.config.page_height_pixels - self.config.bottom_margin_pixels - page_number_image.height,
                )
            self.base_image.paste(
                im=page_number_image,
                box=page_number_location,
                mask=page_number_image,
            )
        if self.print_debug:
            self.draw.line(
                [(left_margin_x_coord, 0), (left_margin_x_coord, self.base_image.height)],
                fill=self.colours["DEBUG_RED"],
                width=2,
            )
            self.draw.line(
                [(right_margin_x_coord, 0), (right_margin_x_coord, self.base_image.height)],
                fill=self.colours["DEBUG_RED"],
                width=2,
            )
            self.draw.line([(0, y_coord), (self.base_image.width, y_coord)], fill=self.colours["DEBUG_RED"], width=2)
            self.draw.line(
                [
                    (0, self.config.page_height_pixels - self.config.bottom_margin_pixels),
                    (self.base_image.width, self.config.page_height_pixels - self.config.bottom_margin_pixels),
                ],
                fill=self.colours["DEBUG_RED"],
                width=2,
            )
            return self.base_image.convert("RGB")
        return self.base_image.convert("CMYK")


class Pages(PrintParams):
    def __init__(
        self, word_search_data: PuzzleData, project_config: ProjectConfig, filename: FilePath, print_debug: bool = False
    ):
        super().__init__(project_config=project_config, print_debug=print_debug)
        self.word_search_data = word_search_data
        self.filename: FilePath = filename
        self.puzzle_pages: list[Image.Image] = []

    def create_and_save_pages(self):
        self.create_pages()
        self.save_pdf()

    def create_pages(self):
        Logger.get_logger().info("Creating pages...")
        if len(self.word_search_data.puzzles) == 0:
            Logger.get_logger().warn("no puzzles in to make in to pages")
            raise ValueError("No puzzles in to make in to pages")
        self._add_front_page()
        self._add_puzzle_pages()
        if len(self.puzzle_pages) % 2 == 0:
            self._add_blank_page()
        set_marker_file(self.filename, int(len(self.puzzle_pages) / self.word_search_data.page_count * 100))
        self._add_solution_pages()
        if len(self.puzzle_pages) % 2 == 1:
            self._add_blank_page()
        set_marker_file(self.filename, int(len(self.puzzle_pages) / self.word_search_data.page_count * 100))

    def _add_solution_pages(self):
        for n in range(0, len(self.word_search_data.puzzles), self.config.solution_per_page):
            Logger.get_logger().info(f"Adding solution page for {n + 1} to {n + self.config.solution_per_page}")
            self.puzzle_pages.append(
                Page(
                    content=ContentsSolution(
                        puzzle_list=self.word_search_data.puzzles[n : n + self.config.solution_per_page],
                        project_config=self.config,
                        print_debug=self.print_debug,
                    ).get_content_image(),
                    page_number=len(self.puzzle_pages) + 1,
                    project_config=self.config,
                    print_debug=self.print_debug,
                ).get_page_image()
            )
            set_marker_file(self.filename, int(len(self.puzzle_pages) / self.word_search_data.page_count * 100))

    def _add_blank_page(self):
        self.puzzle_pages.append(
            Page(
                content=ContentsBlank(project_config=self.config).get_content_image(),
                page_number=len(self.puzzle_pages) + 1,
                project_config=self.config,
                print_debug=self.print_debug,
            ).get_page_image()
        )

    def _add_puzzle_pages(self):
        for puzzle in self.word_search_data.puzzles:
            Logger.get_logger().info(f"Adding puzzle page for {puzzle.display_title}")
            layout = puzzle.get_puzzle_layout()
            self.puzzle_pages.append(
                Page(
                    content=ContentsPuzzleGrid(
                        puzzle=puzzle, grid_page_type=layout, project_config=self.config, print_debug=self.print_debug
                    ).get_content_image(),
                    page_number=len(self.puzzle_pages) + 1,
                    project_config=self.config,
                    print_debug=self.print_debug,
                ).get_page_image()
            )
            if layout == LayoutEnum.DOUBLE:
                self.puzzle_pages.append(
                    Page(
                        content=ContentsPuzzleWordlist(
                            puzzle=puzzle, project_config=self.config, print_debug=self.print_debug
                        ).get_content_image(),
                        page_number=len(self.puzzle_pages) + 1,
                        project_config=self.config,
                        print_debug=self.print_debug,
                    ).get_page_image()
                )
            Logger.get_logger().debug(f"Added puzzle page for {puzzle.display_title}")
            set_marker_file(self.filename, int(len(self.puzzle_pages) / self.word_search_data.page_count * 100))

    def _add_front_page(self):
        self.puzzle_pages.append(
            Page(
                content=ContentsFront(project_config=self.config, print_debug=self.print_debug).get_content_image(),
                page_number=len(self.puzzle_pages) + 1,
                project_config=self.config,
                print_debug=self.print_debug,
            ).get_page_image()
        )
        set_marker_file(self.filename, int(len(self.puzzle_pages) / self.word_search_data.page_count * 100))

    def save_pdf(self):
        if len(self.puzzle_pages) <= 0:
            raise ValueError("No puzzles in to save to pdf")
        self.puzzle_pages[0].save(
            self.filename,
            format="PDF",
            save_all=True,
            append_images=self.puzzle_pages[1:],
            resolution=self.config.dpi,
            title=self.word_search_data.book_title,
        )
        Logger.get_logger().info(f"Saved to {self.filename}")
        clear_marker_file(self.filename)
