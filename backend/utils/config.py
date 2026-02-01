from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """Configuration settings for the backend application."""

    log_level: str = Field(default="INFO", description="The log level for the application.")
    data_folder: str = Field(default="data", description="The data folder for the application.")
    archive_folder: str = Field(default="archive", description="The archive folder for the application.")
    project_settings: str = Field(default="project_settings.json", description="The project config file.")
    input_filename: str = Field(default="wordlist.json", description="The input file for the application.")
    data_filename: str = Field(default="puzzledata.json", description="The data file for the application.")
    output_filename: str = Field(default="manuscript.pdf", description="The output file for the application.")
    frontend_host_for_cors: str = Field(default="http://localhost:5001", description="The frontend host for CORS.")


class AIConfig(BaseModel):
    """Configuration settings for AI."""

    model: str = Field(default="claude-haiku-4-5", description="AI model to use for puzzle generation")
    api_key: str = Field(default="", description="API key for LLM")


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env", extra="ignore")
    """Application configuration settings."""

    app: AppConfig = AppConfig()
    ai: AIConfig = AIConfig()
