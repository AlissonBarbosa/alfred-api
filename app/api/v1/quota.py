from fastapi import APIRouter, HTTPException, Query, status, Depends
from openstack import exceptions as os_exceptions
from typing import List

from app.schemas.quota import ProjectQuotaResponse, TenantQuotaResponse
from app.services.openstack_client import OpenstackService, get_openstack_service
from app.api.dependecies import get_matched_projects
import logging

router = APIRouter(prefix="/api/v1/quota", tags=["quota"])
logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=TenantQuotaResponse,
    summary="Get quotas for all projects of a tenant")
async def get_tenant_quota(
  projects: List = Depends(get_matched_projects),
  os_svc: OpenstackService = Depends(get_openstack_service),
):
  try:
    logger.info("Fetching quota for tenant")
    quota_list = []
    for proj in projects:
      data = os_svc.get_quota(proj)
      quota_list.append(data)
    return TenantQuotaResponse(projects_quotas=quota_list)
  except os_exceptions.ResourceNotFound as e:
    logger.warning("Resource not found: %s", str(e))
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=str(e)
    )
  except os_exceptions.HttpException as e:
    logger.error("HTTP error: %s", str(e))
    if getattr(e, "status_code", None) == status.HTTP_401_UNAUTHORIZED:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized access to OpenStack API"
      )
    raise HTTPException(
      status_code=getattr(e, "status_code", status.HTTP_502_BAD_GATEWAY),
      detail=e.message or "Failed to connect to OpenStack API"
    )
  except Exception as e:
    logger.exception("Unexpected error: %s", str(e))
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="An unexpected error occurred while fetching quota"
    )