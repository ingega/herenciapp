from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_main():
    # Act: Send a GET request to the root
    response = client.get("/")
    
    # Assert: Status code is 200 (OK)
    assert response.status_code == 200
    
    # Assert: Check if our brand name is in the HTML response
    assert "Herencia del Abuelo" in response.text
    
    # Assert: Verify it's returning HTML, not just JSON
    assert "text/html" in response.headers["content-type"]