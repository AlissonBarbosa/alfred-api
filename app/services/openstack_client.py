import openstack
from openstack import exceptions
from openstack.identity.v3.project import Project
from fastapi import Query
import logging
import re

logger = logging.getLogger(__name__)

class OpenstackService:
  def __init__(self, cloud: str):
    self.conn = openstack.connect(cloud=cloud)
    self.cloud = cloud

  def get_projects_by_tenant_id(self, tenantID: str) -> list[Project]:
    all_projects = list(self.conn.identity.projects())
    regex = re.compile(tenantID)
    matched = [p for p in all_projects if regex.search(p.name)]
    if not matched:
      raise exceptions.ResourceNotFound(f"no projects found for this tenant '{tenantID}' in region '{self.cloud}'.")
    logger.debug("projecs founded: %s", [p.name for p in matched])
    return matched

  def get_quota(self, project: Project) -> dict:
    compute_quota = self.conn.compute.get_quota_set(project.id)
    network_quota = self.conn.network.get_quota(project.id)
    volume_quota = self.conn.block_storage.get_quota_set(project.id)
    return {
      "project_id": project.id,
      "project_name": project.name,
      "region": self.cloud,
      "compute": compute_quota.to_dict(),
      "network": network_quota.to_dict(),
      "volume": volume_quota.to_dict(),
    }

def get_openstack_service(
    region: str = Query(
      ...,
      min_length=1,
      description="Region name to connect to OpenStack"
    )
) -> OpenstackService:
  """
  Create an OpenstackService instance with the specified cloud name.
  """
  return OpenstackService(cloud=region)