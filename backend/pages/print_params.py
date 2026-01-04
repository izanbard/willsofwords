from PIL import ImageFont, Image

from backend.models.config import Config


class PrintParams:
    def __init__(self) -> None:
        self.config: Config = Config()
        self.size: tuple[int, int] = (0, 0)
        if self.config.PRINT_DEBUG:
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
            "TITLE_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.config.PRINT_TITLE_FONT_SIZE_PIXELS),
            "HEADING_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.PRINT_LONG_FACT_HEADING_FONT_SIZE_PIXELS
            ),
            "CONTENT_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.PRINT_LONG_FACT_CONTENT_FONT_SIZE_PIXELS
            ),
            "CELL_FONT": ImageFont.truetype("backend/assets/verdana.ttf", size=self.config.PRINT_CELL_FONT_SIZE_PIXELS),
            "SEARCH_LIST_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.PRINT_WORDLIST_FONT_SIZE_PIXELS + 1
            ),
            "PAGE_NUMBER_FONT": ImageFont.truetype(
                "backend/assets/verdana.ttf", size=self.config.PRINT_PAGE_NUMBER_FONT_SIZE_PIXELS
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
