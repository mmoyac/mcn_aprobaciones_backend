"""
Tests para endpoints de usuarios
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_listar_usuarios():
    """Test para listar usuarios"""
    response = client.get("/api/v1/usuarios/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Verificar que no se incluya la contraseña
    if len(data) > 0:
        assert "UserCd" in data[0]
        assert "UserDs" in data[0]
        assert "UserLlave" not in data[0]  # Contraseña NO debe estar


def test_listar_usuarios_con_paginacion():
    """Test para paginación de usuarios"""
    response = client.get("/api/v1/usuarios/?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_listar_usuarios_limite_excedido():
    """Test para verificar límite máximo"""
    response = client.get("/api/v1/usuarios/?limit=2000")
    assert response.status_code == 400
    assert "límite máximo" in response.json()["detail"].lower()


def test_contar_usuarios():
    """Test para contar usuarios"""
    response = client.get("/api/v1/usuarios/count")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert isinstance(data["total"], int)
    assert data["total"] >= 0
