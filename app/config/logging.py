import logging.config
from pythonjsonlogger import json

def get_logging_config(debug: bool) -> dict:
  level = "DEBUG" if debug else "INFO"
  return {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
      "json": {
        "()": json.JsonFormatter,
        "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
      },
    },
    "handlers": {
      "console": {
        "class": "logging.StreamHandler",
        "formatter": "json",
        "level": level,
        "stream": "ext://sys.stdout",
      }
    },
    "root": {
      "handlers": ["console"],
      "level": level,
    },
    "loggers": {
      "app": {
        "handlers": ["console"],
        "level": level,
        "propagate": False,
      },
      "uvicorn.access": {
        "handlers": ["console"],
        "level": level,
        "propagate": False,
      },
      "uvicorn.error": {
        "handlers": ["console"],
        "level": level,
        "propagate": False,
      },
      "fastapi": {
        "handlers": ["console"],
        "level": level,
        "propagate": False,
      },
    },
  }