import openstack
from openstack import exceptions
from fastapi import Query
import logging

logger = logging.getLogger(__name__)

class OpenstackService:
  def __init__(self, cloud: str):
    self.conn = openstack.connect(cloud=cloud)
    self.cloud = cloud

  def get_quota(self, project_name: str) -> dict:
    project = self.conn.identity.find_project(project_name)
    if not project:
      raise exceptions.ResourceNotFound(
        f"project '{project_name}' not found in cloud '{self.cloud}'."
      )
    compute_quota = self.conn.compute.get_quota_set(project.id)
    network_quota = self.conn.network.get_quota(project.id)
    volume_quota = self.conn.block_storage.get_quota_set(project.id)
    return {
      "project_name": project_name,
      "cloud": self.cloud,
      "compute": compute_quota.to_dict(),
      "network": network_quota.to_dict(),
      "volume": volume_quota.to_dict(),
    }

def get_openstack_service(
    cloud: str = Query(
      ...,
      min_length=1,
      description="Cloud name to connect to OpenStack"
    )
) -> OpenstackService:
  """
  Create an OpenstackService instance with the specified cloud name.
  """
  return OpenstackService(cloud)