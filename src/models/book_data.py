from pathlib import Path


from PIL import Image, ImageDraw, ImageFont, ImageText, ImageOps
from pydantic import BaseModel, Field

from src.models import Size, Puzzle, Wordlist, Category
from src.models.config import Config
from src.utils import Logger


class BookData(BaseModel):
    book_title: str = Field(..., description="Title of the book")
    wordlist: Wordlist = Field(..., description="List of words provided from LLM")
    puzzles: dict[str, Puzzle] = Field(default_factory=dict, description="List of created Puzzles")

    def create_puzzles(self) -> None:
        Logger.get_logger().info("Creating puzzles")
        for category in self.wordlist.category_list:
            self._add_a_puzzle(category)
        Logger.get_logger().info("Completed creating puzzles")

    def save_data(self, filename: Path) -> None:
        Logger.get_logger().info(f"Saving puzzles to {filename}")
        with open(filename, "w") as fd:
            fd.write(self.model_dump_json(indent=2))
        Logger.get_logger().info(f"Done saving puzzles to {filename}")

    def create_pages(self, filename: Path):
        Logger.get_logger().info("Creating pages...")
        if len(self.puzzles) == 0:
            Logger.get_logger().warn("no puzzles in to make in to pages")
            return

        content_sizes: list[tuple[str, int]] = []

        for name, puzzle in self.puzzles.items():
            content_sizes.append((name, puzzle.content_image_count()))
        content_sizes = self._check_fix_puzzle_order(content_sizes)

        puzzle_pages: list[Image.Image] = []
        solution_images: list[Image.Image] = []
        puzzle_pages.append(self.create_front_page(len(puzzle_pages) + 1))
        solution_images.append(self.create_solution_front_image())

        solutions_cache: list[Image.Image] = []
        for puzzle_number, puzzle_size_tuple in enumerate(content_sizes, 1):
            for image in self.puzzles[puzzle_size_tuple[0]].create_page_content(puzzle_number):
                puzzle_pages.append(self.create_page(image, len(puzzle_pages) + 1))
            Logger.get_logger().info(f"{self.puzzles[puzzle_size_tuple[0]].puzzle_title:<25} -> pages created")
            solutions_cache.append(self.puzzles[puzzle_size_tuple[0]].create_solution_page_content(puzzle_number))
            if len(solutions_cache) == Config.PRINT_SOLUTION_PER_PAGE:
                solution_images.append(self.create_solutions_content(solutions_cache))
                solutions_cache = []
        if len(solutions_cache) > 0:
            solution_images.append(self.create_solutions_content(solutions_cache))
        if len(puzzle_pages) % 2 != 0:
            puzzle_pages.append(self.create_blank_page(len(puzzle_pages) + 1))
        Logger.get_logger().info("Creating solutions pages...")
        for solution_image in solution_images:
            puzzle_pages.append(self.create_page(solution_image, len(puzzle_pages) + 1))
        if len(puzzle_pages) % 2 != 0:
            puzzle_pages.append(self.create_blank_page(len(puzzle_pages) + 1))
        Logger.get_logger().info("Wrapping it all up in a bow...")
        self.save_pdf(filename, puzzle_pages)
        Logger.get_logger().info(
            f"Pages complete, {len(self.puzzles):02g} puzzles and solutions " f"in {len(puzzle_pages):03g} pages"
        )

    def save_pdf(self, filename: Path, puzzle_pages: list[Image.Image]):
        if Config.PRINT_DEBUG:
            filename = filename.with_stem(filename.stem + "_PRINT_DEBUG")
        puzzle_pages[0].save(
            filename,
            format="PDF",
            save_all=True,
            append_images=puzzle_pages[1:],
            resolution=Config.PRINT_DPI,
            title=self.book_title,
        )
        Logger.get_logger().info(f"Saved to {filename}")

    def create_front_page(self, page_number: int) -> Image.Image:
        content = Image.new(
            mode="LA", size=(Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_CONTENT_HEIGHT_PIXELS), color=(0, 0)
        )
        draw = ImageDraw.Draw(content)
        draw.text(
            xy=(Config.PRINT_CONTENT_WIDTH_PIXELS // 2, Config.PRINT_CONTENT_HEIGHT_PIXELS // 2),
            text="A Glorious Front Page Goes Here",
            fill=(0, 255),
            font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_TITLE_FONT_SIZE),
            anchor="mm",
            align="centre",
        )
        return self.create_page(content, page_number)

    @staticmethod
    def create_solution_front_image() -> Image.Image:
        content = Image.new(
            mode="LA", size=(Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_CONTENT_HEIGHT_PIXELS), color=(0, 0)
        )
        draw = ImageDraw.Draw(content)
        draw.text(
            xy=(Config.PRINT_CONTENT_WIDTH_PIXELS // 2, Config.PRINT_CONTENT_HEIGHT_PIXELS // 2),
            text="The Solutions you seek are here",
            fill=(0, 255),
            font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_TITLE_FONT_SIZE),
            anchor="mm",
            align="centre",
        )
        return content

    def create_blank_page(self, page_number: int) -> Image.Image:
        blank_content = Image.new(
            mode="LA",
            size=(
                Config.PRINT_CONTENT_WIDTH_PIXELS,
                Config.PRINT_CONTENT_HEIGHT_PIXELS,
            ),
            color=255,
        )

        return self.create_page(blank_content, page_number)

    def create_page_number_image(self, page_number: str) -> Image.Image:
        text = ImageText.Text(
            text=page_number, font=ImageFont.truetype("src/assets/verdana.ttf", size=Config.PRINT_CELL_FONT_SIZE_PIXELS)
        )
        page_number = Image.new("LA", [int(x) for x in text.get_bbox()[2:]], color=(0, 0))
        draw = ImageDraw.Draw(page_number)
        draw.text((page_number.width // 2, page_number.height // 2), text, anchor="mm", fill=(0, 255))
        return page_number

    def create_page(self, content: Image.Image, page_number: int) -> Image.Image:
        is_even = page_number % 2 == 0
        page = Image.new(
            mode="LA",
            size=(
                Config.PRINT_PAGE_WIDTH_PIXELS,
                Config.PRINT_PAGE_HEIGHT_PIXELS,
            ),
            color=255,
        )
        if is_even:
            left_margin_x_coord = Config.PRINT_OUTER_MARGIN_PIXELS
            right_margin_x_coord = Config.PRINT_PAGE_WIDTH_PIXELS - Config.PRINT_INNER_MARGIN_PIXELS
        else:
            left_margin_x_coord = Config.PRINT_INNER_MARGIN_PIXELS
            right_margin_x_coord = Config.PRINT_PAGE_WIDTH_PIXELS - Config.PRINT_OUTER_MARGIN_PIXELS
        y_coord = Config.PRINT_TOP_MARGIN_PIXELS
        page.paste(content, (left_margin_x_coord, y_coord), content)
        if page_number > 1:
            page_number = self.create_page_number_image(str(page_number))
            page.paste(
                page_number,
                (
                    left_margin_x_coord if is_even else (right_margin_x_coord - page_number.width),
                    Config.PRINT_PAGE_HEIGHT_PIXELS - Config.PRINT_BOTTOM_MARGIN_PIXELS - page_number.height,
                ),
                page_number,
            )
        if Config.PRINT_DEBUG:
            page = page.convert("RGB")
            draw = ImageDraw.Draw(page)
            draw.line([(left_margin_x_coord, 0), (left_margin_x_coord, page.height)], fill=(255, 0, 0), width=2)
            draw.line([(right_margin_x_coord, 0), (right_margin_x_coord, page.height)], fill=(255, 0, 0), width=2)
            draw.line([(0, y_coord), (page.width, y_coord)], fill=(255, 0, 0), width=2)
            draw.line(
                [
                    (0, Config.PRINT_PAGE_HEIGHT_PIXELS - Config.PRINT_BOTTOM_MARGIN_PIXELS),
                    (page.width, Config.PRINT_PAGE_HEIGHT_PIXELS - Config.PRINT_BOTTOM_MARGIN_PIXELS),
                ],
                fill=(255, 0, 0),
                width=2,
            )

            draw.line(
                [
                    (left_margin_x_coord, Config.PRINT_TOP_MARGIN_PIXELS + Config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                    (right_margin_x_coord, Config.PRINT_TOP_MARGIN_PIXELS + Config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                ],
                fill=(0, 255, 0),
                width=2,
            )
            draw.line(
                [
                    (
                        left_margin_x_coord,
                        Config.PRINT_CONTENT_HEIGHT_PIXELS
                        + Config.PRINT_TOP_MARGIN_PIXELS
                        - Config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS,
                    ),
                    (
                        right_margin_x_coord,
                        Config.PRINT_CONTENT_HEIGHT_PIXELS
                        + Config.PRINT_TOP_MARGIN_PIXELS
                        - Config.PRINT_WORDLIST_BOX_HEIGHT_PIXELS,
                    ),
                ],
                fill=(0, 255, 0),
                width=2,
            )
            draw.line(
                [
                    (
                        left_margin_x_coord,
                        ((Config.PRINT_CONTENT_HEIGHT_PIXELS - Config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2)
                        + (Config.PRINT_TOP_MARGIN_PIXELS + Config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                    ),
                    (
                        right_margin_x_coord,
                        ((Config.PRINT_CONTENT_HEIGHT_PIXELS - Config.PRINT_TITLE_BOX_HEIGHT_PIXELS) // 2)
                        + (Config.PRINT_TOP_MARGIN_PIXELS + Config.PRINT_TITLE_BOX_HEIGHT_PIXELS),
                    ),
                ],
                fill=(255, 153, 51),
                width=2,
            )

            return page
        return page.convert("L")

    def create_solutions_content(self, cache: list[Image.Image]) -> Image.Image:
        if len(cache) > Config.PRINT_SOLUTION_PER_PAGE:
            raise RuntimeError("too many solutions for page")
        content = Image.new(
            mode="LA", size=(Config.PRINT_CONTENT_WIDTH_PIXELS, Config.PRINT_CONTENT_HEIGHT_PIXELS), color=(0, 0)
        )

        col_width = Config.PRINT_CONTENT_WIDTH_PIXELS // Config.PRINT_SOLUTION_PAGE_COLS
        row_height = Config.PRINT_CONTENT_HEIGHT_PIXELS // Config.PRINT_SOLUTION_PAGE_ROWS
        n = 0
        for y in range(Config.PRINT_SOLUTION_PAGE_ROWS):
            for x in range(Config.PRINT_SOLUTION_PAGE_COLS):
                if n >= len(cache):
                    continue
                sln = ImageOps.contain(
                    image=cache[n],
                    size=(
                        Config.PRINT_CONTENT_WIDTH_PIXELS // Config.PRINT_SOLUTION_PAGE_COLS,
                        Config.PRINT_CONTENT_HEIGHT_PIXELS // Config.PRINT_SOLUTION_PAGE_ROWS,
                    ),
                )
                content.paste(sln, ((x * col_width) + (col_width // 2) - (sln.width // 2), y * row_height), sln)
                n += 1
        return content

    def _add_a_puzzle(self, category: Category) -> None:
        Logger.get_logger().debug(f"Creating puzzle: {category.category}")
        len_words = sum(len(word) for word in category.word_list)
        size = Size(len_words, Config.PUZZLE_MAX_DENSITY)
        Logger.get_logger().debug(f"Puzzle Target Size: {size.columns}x{size.rows}")
        puzzle = Puzzle(
            puzzle_title=category.category,
            input_word_list=category.word_list,
            columns=size.columns,
            rows=size.rows,
        )
        puzzle.populate_puzzle()
        count = 1
        while puzzle.density < Config.PUZZLE_MIN_DENSITY:
            Logger.get_logger().debug(f"Puzzle failed density check, trying again, actual density: {puzzle.density}")
            if count % 5 == 0:
                Logger.get_logger().debug("Reducing size of Puzzle before retry")
                if puzzle.rows > puzzle.columns:
                    puzzle.change_puzzle_size(puzzle.rows - 1, puzzle.columns)
                else:
                    puzzle.change_puzzle_size(puzzle.rows, puzzle.columns - 1)
            else:
                puzzle.puzzle_reset()
            puzzle.populate_puzzle()
            count += 1
        Logger.get_logger().info(
            f"{puzzle.puzzle_title:<25} -> {len(puzzle.puzzle_word_list):02g} words out "
            f"of {len(puzzle.input_word_list):02g}, size {puzzle.columns:02g}x{puzzle.rows:02g} with "
            f"a density of {puzzle.density:.2%}"
        )
        self.puzzles[puzzle.puzzle_title] = puzzle

    @staticmethod
    def _check_fix_puzzle_order(content_size_list: list[tuple[str, int]]) -> list[tuple[str, int]]:
        if sum(1 for x in content_size_list if x[1] == 2) == 0:
            return content_size_list
        length = len(content_size_list)
        single_count = 0
        index = 0
        while index < length:
            if content_size_list[index][1] == 1:
                single_count += 1
                index += 1
            elif content_size_list[index][1] == 2:
                if single_count % 2 != 0:
                    content_size_list[index], content_size_list[index - 1] = (
                        content_size_list[index - 1],
                        content_size_list[index],
                    )
                    single_count -= 1
                else:
                    index += 1
        return content_size_list
