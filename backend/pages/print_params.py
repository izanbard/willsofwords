from PIL import ImageFont, Image

from backend.models import ProjectConfig


class PrintParams:
    def __init__(self, *, project_config: ProjectConfig) -> None:
        self.config: ProjectConfig = project_config

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
            "TITLE_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.config.title_font_size_pixels),
            "HEADING_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.config.long_fact_line_spacing_pixels),
            "CONTENT_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.long_fact_content_font_size_pixels
            ),
            "CELL_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.config.cell_font_size_pixels),
            "CELL_DEBUG_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.config.cell_font_size_pixels // 2),
            "SEARCH_LIST_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.wordlist_font_size_pixels + 1
            ),
            "PAGE_NUMBER_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.page_number_font_size_pixels
            ),
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
