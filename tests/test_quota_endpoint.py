# tests/test_quota_endpoint.py

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from openstack import exceptions as os_exceptions

# 1. Importa o router e as dependências a sobrescrever
from app.api.v1.quota import router
from app.api.dependecies import get_matched_projects
from app.services.openstack_client import get_openstack_service

# 2. Cria uma instância mínima de FastAPI e inclui o router
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# 3. Overriding global para sempre retornar dois projetos
app.dependency_overrides[get_matched_projects] = lambda: ["projA", "projB"]


# 4. Dummy services simulando cada cenário de resposta do OpenstackService
class DummyServiceSuccess:
    def get_quota(self, project_id: str):
        # Deve corresponder ao schema ProjectQuotaResponse
        return {
            "project_id": project_id,
            "project_name": f"name-of-{project_id}",
            "region": "RegionTest",
            "compute": {"cores": 4, "instances": 2},
            "network": {"floating_ips": 3},
            "volume": {"volumes": 5},
        }


class DummyService404:
    def get_quota(self, project_id: str):
        raise os_exceptions.ResourceNotFound("projeto não encontrado")


class DummyService401:
    def get_quota(self, project_id: str):
        ex = os_exceptions.HttpException("token inválido")
        ex.status_code = status.HTTP_401_UNAUTHORIZED
        ex.http_status = status.HTTP_401_UNAUTHORIZED
        raise ex


class DummyService502:
    def get_quota(self, project_id: str):
        ex = os_exceptions.HttpException("bad gateway")
        ex.status_code = status.HTTP_502_BAD_GATEWAY
        ex.http_status = status.HTTP_502_BAD_GATEWAY
        raise ex


class DummyService500:
    def get_quota(self, project_id: str):
        raise Exception("erro inesperado")


# 5. Fixture autouse para limpar overrides de get_openstack_service antes/depois de cada teste
@pytest.fixture(autouse=True)
def clear_openstack_override():
    app.dependency_overrides.pop(get_openstack_service, None)
    yield
    app.dependency_overrides.pop(get_openstack_service, None)


def test_get_quota_success():
    # Arrange: força o uso do DummyServiceSuccess
    app.dependency_overrides[get_openstack_service] = lambda: DummyServiceSuccess()

    # Act: chamada ao endpoint
    response = client.get("/api/v1/quota/")

    # Assert: 200 OK e payload conforme TenantQuotaResponse
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "projects_quotas" in body
    assert isinstance(body["projects_quotas"], list)
    assert len(body["projects_quotas"]) == 2

    # verifica campos de cada ProjectQuotaResponse
    for idx, proj in enumerate(["projA", "projB"]):
        item = body["projects_quotas"][idx]
        assert item["project_id"] == proj
        assert item["project_name"] == f"name-of-{proj}"
        assert item["region"] == "RegionTest"
        assert "compute" in item and "network" in item and "volume" in item


def test_get_quota_not_found():
    # Arrange: simula ResourceNotFound → 404
    app.dependency_overrides[get_openstack_service] = lambda: DummyService404()

    # Act
    response = client.get("/api/v1/quota/")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "projeto não encontrado"}


def test_get_quota_unauthorized():
    # Arrange: simula HttpException 401 → 401
    app.dependency_overrides[get_openstack_service] = lambda: DummyService401()

    # Act
    response = client.get("/api/v1/quota/")

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized access to OpenStack API"}


def test_get_quota_http_error_other():
    # Arrange: simula HttpException 502 → 502
    app.dependency_overrides[get_openstack_service] = lambda: DummyService502()

    # Act
    response = client.get("/api/v1/quota/")

    # Assert
    assert response.status_code == 502
    assert response.json() == {"detail": "bad gateway"}


def test_get_quota_unexpected_error():
    # Arrange: simula erro genérico → 500
    app.dependency_overrides[get_openstack_service] = lambda: DummyService500()

    # Act
    response = client.get("/api/v1/quota/")

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "detail": "An unexpected error occurred while fetching quota"
    }
