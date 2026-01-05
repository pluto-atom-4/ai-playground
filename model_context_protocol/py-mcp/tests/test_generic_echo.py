import pytest
from fastapi.testclient import TestClient
from generic_echo import app

client = TestClient(app)


def test_echo_logic():
    """Directly test the endpoint that the MCP tool is wrapping."""
    test_msg = "Test Message"
    response = client.post("/echo", params={"message": test_msg})

    assert response.status_code == 200
    assert response.json()["echo"] == test_msg


def test_echo_with_json_body():
    """Test echo endpoint with message in request body."""
    test_msg = "Hello MCP"
    # FastAPI can also accept query params or JSON body
    response = client.post("/echo?message=" + test_msg)

    assert response.status_code == 200
    assert response.json()["echo"] == test_msg


def test_echo_special_characters():
    """Test echo endpoint with special characters."""
    test_msg = "Special: !@#$%^&*()"
    response = client.post("/echo", params={"message": test_msg})

    assert response.status_code == 200
    assert response.json()["echo"] == test_msg
