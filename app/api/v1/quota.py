from fastapi import APIRouter, HTTPException, Query, status, Depends
from openstack import exceptions as os_exceptions

from app.schemas.quota import QuotaResponse
from app.services.openstack_client import OpenstackService, get_openstack_service
import logging

router = APIRouter(prefix="/api/v1/quota", tags=["quota"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=QuotaResponse)
async def get_quota(
  tenant_name: str = Query(
    ..., min_length=1, description="Tenant name to get quota for"
  ),
  os_svc: OpenstackService = Depends(get_openstack_service),
):
  try:
    logger.info("Fetching quota for tenant: %s", tenant_name)
    return os_svc.get_quota(tenant_name)
  except os_exceptions.ResourceNotFound as e:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=str(e)
    )
  except os_exceptions.HttpException as e:
    if e.http_status == status.HTTP_401_UNAUTHORIZED:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized access to OpenStack API"
      )
    raise HTTPException(
      status_code=e.http_status or status.HTTP_502_BAD_GATEWAY,
      detail=e.message or "Failed to connect to OpenStack API"
    )
  except Exception:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="An unexpected error occurred while fetching quota"
    )