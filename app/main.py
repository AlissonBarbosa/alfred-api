from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.v1.quota import router as quota_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
  app = FastAPI(
    title= "Openstack management API - Alfred",
    version= "0.0.1",
    description= "API for managing Openstack resources",
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