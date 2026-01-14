from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """Configuration settings for the backend application."""

    log_level: str = Field(default="INFO", description="The log level for the application.")
    input_filename: str = Field(default="wordlist.json", description="The input file for the application.")
    data_filename: str = Field(default="puzzledata.json", description="The data file for the application.")
    output_filename: str = Field(default="manuscript.pdf", description="The output file for the application.")
    frontend_host_for_cors: str = Field(default="http://localhost:5001", description="The frontend host for CORS.")


class AIConfig(BaseModel):
    """Configuration settings for AI."""

    model: str = Field(default="gemma3:12b", description="AI model to use for puzzle generation")
    host: str = Field(default="http://localhost:11434/", description="AI host URL for puzzle generation")


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=".env", extra="ignore")
    """Application configuration settings."""

    app: AppConfig
    ai: AIConfig
