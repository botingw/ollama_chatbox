import pytest
from fastapi.testclient import TestClient
from app.main import app
import httpx
from unittest.mock import patch, MagicMock

client = TestClient(app)

@pytest.fixture
def mock_ollama_response():
    return {
        "response": "This is a test response",
        "model": "smollm2:135m"
    }

@pytest.fixture
def mock_models_response():
    return {
        "models": [
            {"name": "smollm2:135m"},
            {"name": "llama2"},
            {"name": "mistral"}
        ]
    }

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_chat_endpoint(mock_ollama_response):
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_ollama_response
        )
        
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello, how are you?",
                "model": "smollm2:135m",
                "stream": False
            }
        )
        
        assert response.status_code == 200
        assert response.json()["response"] == "This is a test response"
        assert response.json()["model"] == "smollm2:135m"

def test_chat_endpoint_error():
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = MagicMock(
            status_code=500,
            json=lambda: {"error": "Internal server error"}
        )
        
        response = client.post(
            "/api/chat",
            json={
                "message": "Hello",
                "model": "smollm2:135m",
                "stream": False
            }
        )
        
        assert response.status_code == 500

def test_list_models_endpoint(mock_models_response):
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_models_response
        )
        
        response = client.get("/api/models")
        
        assert response.status_code == 200
        assert len(response.json()["models"]) == 3
        assert response.json()["models"][0]["name"] == "smollm2:135m"

def test_list_models_endpoint_error():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=500,
            json=lambda: {"error": "Internal server error"}
        )
        
        response = client.get("/api/models")
        
        assert response.status_code == 500 