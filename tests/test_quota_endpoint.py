import pytest
from fastapi.testclient import TestClient
from fastapi import status
from openstack import exceptions as os_exceptions

from app.main import create_app

client = TestClient(create_app())

def test_read_quota_success(monkeypatch):
  fake_quota = {
    "project_name": "test_project",
    "cloud": "RegionOne",
    "compute": {"cores": 10, "instances": 5},
    "network": {"networks": 3, "subnets": 4},
    "volume": {"volumes": 2, "gigabytes": 100},
  }

  monkeypatch.setattr(
    "app.services.openstack_client.OpenstackService.__init__",
    lambda self, cloud: None
  )

  monkeypatch.setattr(
    "app.services.openstack_client.OpenstackService.get_quota",
    lambda self, project_name: fake_quota
  )

  response = client.get(
    "/api/v1/quota/",
    params={"tenant_name": "test_project", "cloud": "RegionOne"},
  )

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == fake_quota

def test_read_quota_not_found(monkeypatch):
  fake_quota = {
    "project_name": "test_project",
    "cloud": "RegionOne",
    "compute": {"cores": 10, "instances": 5},
    "network": {"networks": 3, "subnets": 4},
    "volume": {"volumes": 2, "gigabytes": 100},
  }

  monkeypatch.setattr(
    "app.services.openstack_client.OpenstackService.__init__",
    lambda self, cloud: None
  )

  monkeypatch.setattr(
    "app.services.openstack_client.OpenstackService.get_quota",
    lambda self, project_name: (_ for _ in ()).throw(
      os_exceptions.ResourceNotFound("Not found")
    )
  )

  response = client.get(
    "/api/v1/quota/",
    params={"tenant_name": "unknown", "cloud": "RegionOne"},
  )

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert response.json() == {"detail": "Not found"}