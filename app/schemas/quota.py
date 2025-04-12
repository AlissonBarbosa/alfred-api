from pydantic import BaseModel

class QuotaResponse(BaseModel):
  project_name: str
  cloud: str
  compute: dict
  network: dict
  volume: dict