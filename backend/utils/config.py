from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """Configuration settings for the backend application."""

    log_level: str = Field(default="INFO", description="The log level for the application.")
    input_filename: str = Field(default="wordlist.json", description="The input file for the application.")
    data_filename: str = Field(default="puzzledata.json", description="The data file for the application.")
    output_filename: str = Field(default="manuscript.pdf", description="The output file for the application.")
    command: str = Field(default="validate_wordlist", description="The command for the application.")


class PrintConfig(BaseModel):
    """Configuration settings for the PDF printing."""

    debug: bool = Field(default=True, description="Print debug mode")
    dpi: int = Field(default=800, description="DPI for the output PDF")
    page_height_inches: float = Field(default=9.61, description="Page height in inches")
    page_width_inches: float = Field(default=6.69, description="Page width in inches")
    top_margin_inches: float = Field(default=0.25, description="Top margin in inches")
    bottom_margin_inches: float = Field(default=0.25, description="Bottom margin in inches")
    outer_margin_inches: float = Field(default=0.25, description="Outer margin in inches")
    inner_margin_inches: float = Field(default=0.75, description="Inner margin in inches")
    title_box_height_inches: float = Field(default=1.0, description="Title box height in inches")
    wordlist_box_height_inches: float = Field(default=2.0, description="Wordlist box height in inches")
    wordlist_font_size_inches: float = Field(default=0.14, description="Wordlist font size in inches")
    wordlist_line_spacing_inches: float = Field(default=0.02, description="Wordlist line spacing in inches")
    grid_pad_inches: float = Field(
        default=0.0, description="Grid padding in inches from the edge of the content box to the borderline"
    )
    grid_border_inches: float = Field(default=0.05, description="Grid border in inches, minimum value for KDP is 0.0125")
    grid_border_radius_inches: float = Field(default=0.15, description="Grid border radius in inches")
    grid_margin_inches: float = Field(
        default=0.15, description="Grid margin in inches from the inside of the border to the edge of the grid"
    )
    cell_font_size_inches: float = Field(default=0.14, description="Cell font size in inches")
    min_cell_size_factor: float = Field(default=1.5, description="Minimum cell size factor")
    variable_cell_size: bool = Field(default=False, description="Enable variable cell size")
    max_cell_size_factor: float = Field(default=2.0, description="Maximum cell size factor")
    long_fact_heading_font_size_inches: float = Field(default=0.28, description="Long fact heading font size in inches")
    long_fact_content_font_size_inches: float = Field(default=0.14, description="Long fact content font size in inches")
    long_fact_line_spacing_inches: float = Field(default=0.02, description="Long fact line spacing in inches")
    page_number_font_size_inches: float = Field(default=0.14, description="Page number font size in inches")
    page_number_offset_inches: float = Field(default=0.1, description="Page number offset in inches")
    solution_page_cols: int = Field(default=2, description="Number of columns for solution pages")
    solution_page_rows: int = Field(default=3, description="Number of rows for solution pages")


class PuzzleConfig(BaseModel):
    """Configuration settings for puzzle generation."""

    max_density: float = Field(default=0.50, description="Maximum density for puzzle generation")
    min_density: float = Field(default=0.30, description="Minimum density for puzzle generation")
    max_placement_attempts: int = Field(
        default=10000, description="Maximum number of placement attempts for puzzle generation"
    )
    enable_profanity_filter: bool = Field(default=True, description="Enable profanity filter for puzzle generation")

    max_columns: int = Field(default=0, description="Maximum number of columns for puzzle generation")
    medium_rows: int = Field(default=0, description="Medium number of rows for puzzle generation")
    max_rows: int = Field(default=0, description="Maximum number of rows for puzzle generation")

    @staticmethod
    def calcualte_ratio(pixels: int, cellsize: int) -> int:
        return pixels // cellsize

    def calculate_column_count(self, grid_width: int, cellsize: int):
        self.max_columns = self.calcualte_ratio(grid_width, cellsize)

    def calculate_medium_row_count(self, grid_height: int, cellsize: int):
        self.medium_rows = self.calcualte_ratio(grid_height, cellsize)

    def calculate_max_row_count(self, grid_height: int, cellsize: int):
        self.max_rows = self.calcualte_ratio(grid_height, cellsize)


class AIConfig(BaseModel):
    """Configuration settings for AI."""

    ai_model: str = Field(default="gemma3:12b", description="AI model to use for puzzle generation")
    ai_host: str = Field(default="http://localhost:11434/", description="AI host URL for puzzle generation")


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env")
    """Application configuration settings."""

    app: AppConfig
    print: PrintConfig
    puzzle: PuzzleConfig
    ai: AIConfig
