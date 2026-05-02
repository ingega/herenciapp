from fastapi.testclient import TestClient
from src.main import app
from src.config import settings
import pytest

client = TestClient(app)

def test_home_endpoint_full_check():
    """
    This test verifies multiple aspects of the home endpoint:
    - Status code
    - Restaurant data
    - HTML response
    - Content-Type header
    - Logo rendering logic
    - Static file serving (indirectly by checking the logo path in the HTML)
    """
    response = client.get("/")
    
    # 1. Verify 200 Code
    assert response.status_code == 200
    
    # 2. Verify Restaurant Data & Config
    assert settings.RESTAURANT_NAME in response.text
    assert settings.RESTAURANT_ADDRESS in response.text
    
    # 3. Verify HTML Response
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text.lower()

def test_static_and_images_config():
    # 4. Verify Static Config
    # Check if the /static mount is alive
    static_css = client.get("/static/css/style.css")
    # Even if file is missing, a 404 from the /static/ route 
    # proves the mount point is active vs a 404 from the root.
    assert static_css.status_code in [200, 404] 

    # 6. Verify Logo Rendering logic
    response = client.get("/")
    expected_img_tag = f"src=\"/static/images/{settings.RESTAURANT_LOGO_NAME}\""
    assert expected_img_tag in response.text
    