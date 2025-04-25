from typing import List
from fastapi import Depends, Query, HTTPException, status

from app.services.openstack_client import OpenstackService, get_openstack_service
from openstack.identity.v3.project import Project
from openstack import exceptions as os_exc

async def get_matched_projects(
    tenantID: str = Query(
      ...,
      min_length=36,
      description="Tenant id pattern to match",
    ),
    os_svc: OpenstackService = Depends(get_openstack_service),
) -> List[Project]:
  try:
    return os_svc.get_projects_by_tenant_id(tenantID)
  except os_exc.ResourceNotFound as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
  except os_exc.HttpException as e:
    code = e.http_status or status.HTTP_502_BAD_GATEWAY
    raise HTTPException(status_code=code, detail=e.message or "Error on OpenStack API")
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Openstack internal error finding projects: {str(e)}")