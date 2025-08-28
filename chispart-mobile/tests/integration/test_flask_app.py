import pytest
import json


class TestFlaskApp:
    def test_homepage(self, app_client):
        """Test página principal"""
        response = app_client.get("/")
        assert response.status_code == 200
        assert b"Chispart" in response.data or b"chispart" in response.data

    def test_chat_page(self, app_client):
        """Test página de chat"""
        response = app_client.get("/chat")
        assert response.status_code == 200

    def test_config_page(self, app_client):
        """Test página de configuración"""
        response = app_client.get("/config")
        assert response.status_code == 200

    def test_about_page(self, app_client):
        """Test página 'Acerca de'"""
        response = app_client.get("/about")
        assert response.status_code == 200
        assert b"Acerca de Chispart Mobile" in response.data

    def test_api_stats(self, app_client):
        """Test endpoint de estadísticas"""
        response = app_client.get("/api/stats")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "app" in data
        assert "version" in data["app"]

    def test_api_config_get(self, app_client):
        """Test GET de configuración"""
        response = app_client.get("/api/config")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "config" in data
        assert "api_providers" in data

    def test_chat_endpoint_empty_message(self, app_client):
        """Test endpoint de chat con mensaje vacío"""
        response = app_client.post(
            "/api/chat", json={"message": ""}, content_type="application/json"
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data
