from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    dpi: int = Field(..., description="DPI for the output PDF")
    page_height_inches: float = Field(..., description="Page height in inches")
    page_width_inches: float = Field(..., description="Page width in inches")
    top_margin_inches: float = Field(..., description="Top margin in inches")
    bottom_margin_inches: float = Field(..., description="Bottom margin in inches")
    outer_margin_inches: float = Field(..., description="Outer margin in inches")
    inner_margin_inches: float = Field(..., description="Inner margin in inches")
    title_box_height_inches: float = Field(..., description="Title box height in inches")
    wordlist_box_height_inches: float = Field(..., description="Wordlist box height in inches")
    wordlist_font_size_inches: float = Field(..., description="Wordlist font size in inches")
    wordlist_line_spacing_inches: float = Field(..., description="Wordlist line spacing in inches")
    grid_pad_inches: float = Field(
        ..., description="Grid padding in inches from the edge of the content box to the borderline"
    )
    grid_border_inches: float = Field(..., description="Grid border in inches, minimum value for KDP is 0.0125")
    grid_border_radius_inches: float = Field(..., description="Grid border radius in inches")
    grid_margin_inches: float = Field(
        ..., description="Grid margin in inches from the inside of the border to the edge of the grid"
    )
    cell_font_size_inches: float = Field(..., description="Cell font size in inches")
    min_cell_size_factor: float = Field(..., description="Minimum cell size factor")
    variable_cell_size: bool = Field(..., description="Enable variable cell size")
    max_cell_size_factor: float = Field(..., description="Maximum cell size factor")
    long_fact_heading_font_size_inches: float = Field(..., description="Long fact heading font size in inches")
    long_fact_content_font_size_inches: float = Field(..., description="Long fact content font size in inches")
    long_fact_line_spacing_inches: float = Field(..., description="Long fact line spacing in inches")
    page_number_font_size_inches: float = Field(..., description="Page number font size in inches")
    page_number_offset_inches: float = Field(..., description="Page number offset in inches")
    solution_page_cols: int = Field(..., description="Number of columns for solution pages")
    solution_page_rows: int = Field(..., description="Number of rows for solution pages")

    @property
    def page_height_pixels(self) -> int:
        return int(self.page_height_inches * self.dpi)

    @property
    def page_width_pixels(self) -> int:
        return int(self.page_width_inches * self.dpi)

    @property
    def top_margin_pixels(self) -> int:
        return int(self.top_margin_inches * self.dpi)

    @property
    def bottom_margin_pixels(self) -> int:
        return int(self.bottom_margin_inches * self.dpi)

    @property
    def outer_margin_pixels(self) -> int:
        return int(self.outer_margin_inches * self.dpi)

    @property
    def inner_margin_pixels(self) -> int:
        return int(self.inner_margin_inches * self.dpi)

    @property
    def content_height_pixels(self) -> int:
        return self.page_height_pixels - self.top_margin_pixels - self.bottom_margin_pixels

    @property
    def content_width_pixels(self) -> int:
        return self.page_width_pixels - self.inner_margin_pixels - self.outer_margin_pixels

    @property
    def title_box_height_pixels(self) -> int:
        return int(self.title_box_height_inches * self.dpi)

    @property
    def title_font_size_pixels(self) -> int:
        return int(self.title_box_height_pixels * 0.3)

    @property
    def wordlist_box_height_pixels(self) -> int:
        return int(self.wordlist_box_height_inches * self.dpi)

    @property
    def wordlist_font_size_pixels(self) -> int:
        return int(self.wordlist_font_size_inches * self.dpi)

    @property
    def wordlist_line_spacing_pixels(self) -> int:
        return int(self.wordlist_line_spacing_inches * self.dpi)

    @property
    def grid_pad_pixels(self) -> int:
        return int(self.grid_pad_inches * self.dpi)

    @property
    def grid_border_pixels(self) -> int:
        return int(self.grid_border_inches * self.dpi)

    @property
    def grid_border_radius_pixels(self) -> int:
        return int(self.grid_border_radius_inches * self.dpi)

    @property
    def grid_margin_pixels(self) -> int:
        return int(self.grid_margin_inches * self.dpi)

    @property
    def grid_width(self) -> int:
        return int(
            self.content_width_pixels
            - (2 * self.grid_pad_pixels)
            - (2 * self.grid_border_pixels)
            - (2 * self.grid_margin_pixels)
        )

    @property
    def grid_height(self) -> int:
        return int(
            self.content_height_pixels
            - (2 * self.grid_pad_pixels)
            - (2 * self.grid_border_pixels)
            - (2 * self.grid_margin_pixels)
            - self.wordlist_box_height_pixels
            - self.title_box_height_pixels
        )

    @property
    def grid_height_two_page(self) -> int:
        return int(
            self.content_height_pixels
            - (2 * self.grid_pad_pixels)
            - (2 * self.grid_border_pixels)
            - (2 * self.grid_margin_pixels)
            - self.title_box_height_pixels
        )

    @property
    def cell_font_size_pixels(self) -> int:
        return int(self.cell_font_size_inches * self.dpi)

    @property
    def min_cell_size(self) -> int:
        return int(self.min_cell_size_factor * self.cell_font_size_pixels)

    @property
    def max_cell_size(self) -> int:
        return int(self.max_cell_size_factor * self.min_cell_size)

    @property
    def long_fact_heading_font_size_pixels(self) -> int:
        return int(self.long_fact_heading_font_size_inches * self.dpi)

    @property
    def long_fact_content_font_size_pixels(self) -> int:
        return int(self.long_fact_content_font_size_inches * self.dpi)

    @property
    def long_fact_line_spacing_pixels(self) -> int:
        return int(self.long_fact_line_spacing_inches * self.dpi)

    @property
    def page_number_font_size_pixels(self) -> int:
        return int(self.page_number_font_size_inches * self.dpi)

    @property
    def page_number_offset_pixels(self) -> int:
        return int(self.page_number_offset_inches * self.dpi)

    @property
    def solution_per_page(self) -> int:
        return self.solution_page_rows * self.solution_page_cols

    max_density: float = Field(..., description="Maximum density for puzzle generation")
    min_density: float = Field(..., description="Minimum density for puzzle generation")
    max_placement_attempts: int = Field(..., description="Maximum number of placement attempts for puzzle generation")
    enable_profanity_filter: bool = Field(..., description="Enable profanity filter for puzzle generation")

    @property
    def max_columns(self) -> int:
        return self.grid_width // self.min_cell_size

    @property
    def medium_rows(self) -> int:
        return self.grid_height // self.min_cell_size

    @property
    def max_rows(self) -> int:
        return self.grid_height_two_page // self.min_cell_size


class ProjectConfigUpdate(BaseModel):
    debug: bool | None = Field(default=None, description="Print debug mode")
    dpi: int | None = Field(default=None, description="DPI for the output PDF")
    page_height_inches: float | None = Field(default=None, description="Page height in inches")
    page_width_inches: float | None = Field(default=None, description="Page width in inches")
    top_margin_inches: float | None = Field(default=None, description="Top margin in inches")
    bottom_margin_inches: float | None = Field(default=None, description="Bottom margin in inches")
    outer_margin_inches: float | None = Field(default=None, description="Outer margin in inches")
    inner_margin_inches: float | None = Field(default=None, description="Inner margin in inches")
    title_box_height_inches: float | None = Field(default=None, description="Title box height in inches")
    wordlist_box_height_inches: float | None = Field(default=None, description="Wordlist box height in inches")
    wordlist_font_size_inches: float | None = Field(default=None, description="Wordlist font size in inches")
    wordlist_line_spacing_inches: float | None = Field(default=None, description="Wordlist line spacing in inches")
    grid_pad_inches: float | None = Field(
        default=None, description="Grid padding in inches from the edge of the content box to the borderline"
    )
    grid_border_inches: float | None = Field(
        default=None, description="Grid border in inches, minimum value for KDP is 0.0125"
    )
    grid_border_radius_inches: float | None = Field(default=None, description="Grid border radius in inches")
    grid_margin_inches: float | None = Field(
        default=None, description="Grid margin in inches from the inside of the border to the edge of the grid"
    )
    cell_font_size_inches: float | None = Field(default=None, description="Cell font size in inches")
    min_cell_size_factor: float | None = Field(default=None, description="Minimum cell size factor")
    variable_cell_size: bool | None = Field(default=None, description="Enable variable cell size")
    max_cell_size_factor: float | None = Field(default=None, description="Maximum cell size factor")
    long_fact_heading_font_size_inches: float | None = Field(default=None, description="Long fact heading font size in inches")
    long_fact_content_font_size_inches: float | None = Field(default=None, description="Long fact content font size in inches")
    long_fact_line_spacing_inches: float | None = Field(default=None, description="Long fact line spacing in inches")
    page_number_font_size_inches: float | None = Field(default=None, description="Page number font size in inches")
    page_number_offset_inches: float | None = Field(default=None, description="Page number offset in inches")
    solution_page_cols: int | None = Field(default=None, description="Number of columns for solution pages")
    solution_page_rows: int | None = Field(default=None, description="Number of rows for solution pages")
    max_density: float | None = Field(default=None, description="Maximum density for puzzle generation")
    min_density: float | None = Field(default=None, description="Minimum density for puzzle generation")
    max_placement_attempts: int | None = Field(
        default=None, description="Maximum number of placement attempts for puzzle generation"
    )
    enable_profanity_filter: bool | None = Field(default=None, description="Enable profanity filter for puzzle generation")
