from pathlib import Path

from PIL import Image, ImageDraw

from src.models import BookData, TitlePageEnum, PageTypeEnum, LayoutEnum
from src.utils import Logger
from .contents import ContentsFront, ContentsBlank, ContentsPuzzleGrid, ContentsPuzzleWordlist, ContentsSolution
from .print_params import PrintParams
from .sub_contents import SubContentsPageNumber


class Page(PrintParams):
    def __init__(self, content: Image.Image, page_number: int) -> None:
        super().__init__()
        self.content: Image.Image = content
        self.page_number: int = page_number
        self.page_type: PageTypeEnum = PageTypeEnum.RECTO if self.page_number % 2 == 1 else PageTypeEnum.VERSO
        self.size = (self.config.PRINT_PAGE_WIDTH_PIXELS, self.config.PRINT_PAGE_HEIGHT_PIXELS)
        self.base_image: Image.Image = self._make_base_image("SOLID_WHITE")
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.base_image)

    def get_page_image(self) -> Image.Image:
        if self.page_type == PageTypeEnum.VERSO:
            left_margin_x_coord = self.config.PRINT_OUTER_MARGIN_PIXELS
            right_margin_x_coord = self.config.PRINT_PAGE_WIDTH_PIXELS - self.config.PRINT_INNER_MARGIN_PIXELS
        else:
            left_margin_x_coord = self.config.PRINT_INNER_MARGIN_PIXELS
            right_margin_x_coord = self.config.PRINT_PAGE_WIDTH_PIXELS - self.config.PRINT_OUTER_MARGIN_PIXELS
        y_coord = self.config.PRINT_TOP_MARGIN_PIXELS
        self.base_image.paste(im=self.content, box=(left_margin_x_coord, y_coord), mask=self.content)
        if self.page_number > 1:
            page_number_image = SubContentsPageNumber(str(self.page_number)).get_content_image()
            if self.page_type == PageTypeEnum.RECTO:
                page_number_location = (
                    right_margin_x_coord - page_number_image.width,
                    self.config.PRINT_PAGE_HEIGHT_PIXELS - self.config.PRINT_BOTTOM_MARGIN_PIXELS - page_number_image.height,
                )
            else:
                page_number_location = (
                    left_margin_x_coord,
                    self.config.PRINT_PAGE_HEIGHT_PIXELS - self.config.PRINT_BOTTOM_MARGIN_PIXELS - page_number_image.height,
                )
            self.base_image.paste(
                im=page_number_image,
                box=page_number_location,
                mask=page_number_image,
            )
        if self.config.PRINT_DEBUG:
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
                    (0, self.config.PRINT_PAGE_HEIGHT_PIXELS - self.config.PRINT_BOTTOM_MARGIN_PIXELS),
                    (self.base_image.width, self.config.PRINT_PAGE_HEIGHT_PIXELS - self.config.PRINT_BOTTOM_MARGIN_PIXELS),
                ],
                fill=self.colours["DEBUG_RED"],
                width=2,
            )
            return self.base_image.convert("RGB")
        return self.base_image.convert("CMYK")


class Pages(PrintParams):
    def __init__(self, book: BookData, filename: Path):
        super().__init__()
        self.book = book
        self.filename: Path = filename if not self.config.PRINT_DEBUG else filename.with_stem(filename.stem + "_PRINT_DEBUG")
        self.puzzle_pages: list[Image.Image] = []

    def create_pages(self):
        Logger.get_logger().info("Creating pages...")
        if len(self.book.puzzles) == 0:
            Logger.get_logger().warn("no puzzles in to make in to pages")
            raise ValueError("No puzzles in to make in to pages")
        self._add_front_page()
        self._add_puzzle_pages()
        if len(self.puzzle_pages) % 2 == 1:
            self._add_blank_page()
        self._add_front_page(TitlePageEnum.SOLUTION)
        self._add_solution_pages()
        if len(self.puzzle_pages) % 2 == 1:
            self._add_blank_page()

    def _add_solution_pages(self):
        for n in range(0, len(self.book.puzzles), self.config.PRINT_SOLUTION_PER_PAGE):
            self.puzzle_pages.append(
                Page(
                    content=ContentsSolution(
                        self.book.puzzles[n : n + self.config.PRINT_SOLUTION_PER_PAGE]
                    ).get_content_image(),
                    page_number=len(self.puzzle_pages) + 1,
                ).get_page_image()
            )

    def _add_blank_page(self):
        self.puzzle_pages.append(
            Page(content=ContentsBlank().get_content_image(), page_number=len(self.puzzle_pages) + 1).get_page_image()
        )

    def _add_puzzle_pages(self):
        for puzzle in self.book.puzzles:
            layout = puzzle.get_puzzle_layout()
            self.puzzle_pages.append(
                Page(
                    content=ContentsPuzzleGrid(puzzle, layout).get_content_image(),
                    page_number=len(self.puzzle_pages) + 1,
                ).get_page_image()
            )
            if layout == LayoutEnum.DOUBLE:
                self.puzzle_pages.append(
                    Page(
                        content=ContentsPuzzleWordlist(puzzle).get_content_image(),
                        page_number=len(self.puzzle_pages) + 1,
                    ).get_page_image()
                )

    def _add_front_page(self, front_page_type: TitlePageEnum = TitlePageEnum.PUZZLE):
        self.puzzle_pages.append(
            Page(
                content=ContentsFront(front_page_type).get_content_image(),
                page_number=len(self.puzzle_pages) + 1,
            ).get_page_image()
        )

    def save_pdf(self):
        if len(self.puzzle_pages) <= 0:
            raise ValueError("No puzzles in to save to pdf")
        self.puzzle_pages[0].save(
            self.filename,
            format="PDF",
            save_all=True,
            append_images=self.puzzle_pages[1:],
            resolution=self.config.PRINT_DPI,
            title=self.book.book_title,
        )
        Logger.get_logger().info(f"Saved to {self.filename}")
