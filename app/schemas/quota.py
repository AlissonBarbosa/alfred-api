from pydantic import BaseModel
from typing import List

class ProjectQuotaResponse(BaseModel):
  project_id: str
  project_name: str
  region: str
  compute: dict
  network: dict
  volume: dict

class TenantQuotaResponse(BaseModel):
  projects_quotas: List[ProjectQuotaResponse]