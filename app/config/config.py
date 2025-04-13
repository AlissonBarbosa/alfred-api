from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field
from typing import List
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
  app_name: str = Field(..., env="APP_NAME")
  version: str = Field(..., env="VERSION")
  description: str = Field(..., env="DESCRIPTION")
  debug: bool = Field(..., env="DEBUG")
  # cors_origins: List[AnyHttpUrl] = Field(..., env="CORS_ORIGINS")

  model_config = SettingsConfigDict(
    env_file = str(BASE_DIR / ".env"),
    env_file_encoding="utf-8",
  )