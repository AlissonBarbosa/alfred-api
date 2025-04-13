from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging.config
from app.api.v1.quota import router as quota_router
from app.config.config import Settings
from app.config.logging import get_logging_config
from functools import lru_cache


@lru_cache()
def get_settings() -> Settings:
  settings = Settings()
  return settings

settings = get_settings()
logging.config.dictConfig(get_logging_config(settings.debug))
logger = logging.getLogger(__name__)
# logger.debug(f"Settings loaded: {settings}")

def create_app() -> FastAPI:
  app = FastAPI(
    title= settings.app_name,
    version= settings.version,
    description= settings.description,
  )

  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
  )

  app.include_router(quota_router)
  return app

app = create_app()