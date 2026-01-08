from PIL import ImageFont, Image

from backend.utils import get_print_config, PrintConfig


class PrintParams:
    def __init__(self) -> None:
        self.config: PrintConfig = get_print_config()

        self.page_height_pixels = int(self.config.page_height_inches * self.config.dpi)
        self.page_width_pixels = int(self.config.page_width_inches * self.config.dpi)
        self.top_margin_pixels = int(self.config.top_margin_inches * self.config.dpi)
        self.bottom_margin_pixels = int(self.config.bottom_margin_inches * self.config.dpi)
        self.outer_margin_pixels = int(self.config.outer_margin_inches * self.config.dpi)
        self.inner_margin_pixels = int(self.config.inner_margin_inches * self.config.dpi)

        self.content_height_pixels = self.page_height_pixels - self.top_margin_pixels - self.bottom_margin_pixels
        self.content_width_pixels = self.page_width_pixels - self.inner_margin_pixels - self.outer_margin_pixels

        self.title_box_height_pixels = int(self.config.title_box_height_inches * self.config.dpi)
        self.title_font_size_pixels = int(self.title_box_height_pixels * 0.3)

        self.wordlist_box_height_pixels = int(self.config.wordlist_box_height_inches * self.config.dpi)
        self.wordlist_font_size_pixels = int(self.config.wordlist_font_size_inches * self.config.dpi)
        self.wordlist_line_spacing_pixels = int(self.config.wordlist_line_spacing_inches * self.config.dpi)

        self.grid_pad_pixels = int(self.config.grid_pad_inches * self.config.dpi)
        self.grid_border_pixels = int(self.config.grid_border_inches * self.config.dpi)
        self.grid_border_radius_pixels = int(self.config.grid_border_radius_inches * self.config.dpi)
        self.grid_margin_pixels = int(self.config.grid_margin_inches * self.config.dpi)
        self.grid_width = (
            self.content_width_pixels
            - (2 * self.grid_pad_pixels)
            - (2 * self.grid_border_pixels)
            - (2 * self.grid_margin_pixels)
        )
        self.grid_height = (
            self.content_height_pixels
            - (2 * self.grid_pad_pixels)
            - (2 * self.grid_border_pixels)
            - (2 * self.grid_margin_pixels)
            - self.wordlist_box_height_pixels
            - self.title_box_height_pixels
        )
        self.grid_height_two_page = (
            self.content_height_pixels
            - (2 * self.grid_pad_pixels)
            - (2 * self.grid_border_pixels)
            - (2 * self.grid_margin_pixels)
            - self.title_box_height_pixels
        )

        self.cell_font_size_pixels = int(self.config.cell_font_size_inches * self.config.dpi)
        self.min_cell_size = int(self.config.min_cell_size_factor * self.cell_font_size_pixels)
        self.max_cell_size = self.config.max_cell_size_factor * self.min_cell_size

        self.long_fact_heading_font_size_pixels = int(self.config.long_fact_heading_font_size_inches * self.config.dpi)
        self.long_fact_content_font_size_pixels = int(self.config.long_fact_content_font_size_inches * self.config.dpi)
        self.long_fact_line_spacing_pixels = int(self.config.long_fact_line_spacing_inches * self.config.dpi)

        self.page_number_font_size_pixels = int(self.config.page_number_font_size_inches * self.config.dpi)
        self.page_number_offset_pixels = int(self.config.page_number_offset_inches * self.config.dpi)

        self.solution_per_page = self.config.solution_page_rows * self.config.solution_page_cols

        self.size: tuple[int, int] = (0, 0)
        if self.config.debug:
            self.mode = "RGBA"
            self.colours: dict[str, tuple[int, int, int, int]] | dict[str, tuple[int, int]] = {
                "DEBUG_BLUE": (0, 0, 255, 255),
                "DEBUG_RED": (255, 0, 0, 255),
                "DEBUG_GREEN": (0, 255, 0, 255),
                "TRANSPARENT_BACKGROUND": (0, 0, 0, 0),
                "SOLID_BLACK": (0, 0, 0, 255),
                "SOLID_WHITE": (255, 255, 255, 255),
            }
        else:
            self.mode = "LA"
            self.colours: dict[str, tuple[int, int, int, int]] | dict[str, tuple[int, int]] = {
                "TRANSPARENT_BACKGROUND": (0, 0),
                "SOLID_BLACK": (0, 255),
                "SOLID_WHITE": (255, 255),
            }

        self.fonts: dict[str, ImageFont.FreeTypeFont] = {
            "TITLE_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.title_font_size_pixels),
            "HEADING_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.long_fact_line_spacing_pixels),
            "CONTENT_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.long_fact_content_font_size_pixels),
            "CELL_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.cell_font_size_pixels),
            "CELL_DEBUG_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.cell_font_size_pixels // 2),
            "SEARCH_LIST_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.wordlist_font_size_pixels + 1),
            "PAGE_NUMBER_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.page_number_font_size_pixels),
        }

    def _make_base_image(self, background: str = None) -> Image.Image:
        if background is None:
            background = "TRANSPARENT_BACKGROUND"
        base_image: Image.Image = Image.new(
            mode=self.mode,
            size=self.size,
            color=self.colours[background],
        )
        return base_image
