import pytest
from fastapi import status

# ==============================================================================
# TEST 1: Unauthenticated User (No Cookie / Missing Credentials)
# ==============================================================================
def test_products_page_unauthenticated_redirects(client):
    """
    Ensure that accessing the protected UI route without an active session
    or auth cookie results in a clean redirect or unauthorized handling.
    """
    # Act: Explicitly prevent following redirects to capture the raw 303 response
    response = client.get("/orders/products/update", follow_redirects=False)
    
    # Assert: Verify authentication blocks the user and pushes them to login
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/auth/login"


# ==============================================================================
# TEST 2: Authenticated User (Cookie present + HTML assertions)
# ==============================================================================
def test_products_page_authenticated_success(client, authorized_client_cookies):
    """
    Ensure that an authorized request loads the products workspace template layout,
    injects session structures safely, and skips auth fallback paths.
    """
    # 1. Mount cookies cleanly on the client instance to clear deprecation warnings 
    # and guarantee middleware visibility.
    client.cookies.update(authorized_client_cookies)
    
    # 2. Act: Set follow_redirects=False. If authentication fails now, 
    # the test will immediately fail with a 303 status code instead of masking it with a 200!
    response = client.get("/orders/products/update", follow_redirects=False)
    
    # Assert 1: Verify it stayed on the products page (No redirection triggered!)
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]
    
    # Assert 2: Jinja Context Inspection
    assert response.context is not None
    assert "config" in response.context
    
    # Assert 3: Text content visual validation
    assert "Comandas" in response.text
    assert "Platillos" in response.text

    # 3. Cleanup client session states for test isolation
    client.cookies.clear()