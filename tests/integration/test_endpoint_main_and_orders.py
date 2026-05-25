import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock
from src.api.v1.auth.auth import create_access_token

@patch("src.api.v1.apps.users.email_service.FastMail.send_message", new_callable=AsyncMock)
class TestProtectedEndpoints:

    def test_unauthorized_redirect_to_login(self, mock_send, client):
        """
        Ensures anonymous users are blocked from secure areas 
        and redirected to the login interface.
        """
        protected_urls = ["/main", "/orders/orders"]
        
        for url in protected_urls:
            # CRITICAL: follow_redirects=False lets us capture the intermediate 303 status
            response = client.get(url, follow_redirects=False)
            
            # Assert that the middleware blocks access with a 303 Redirect
            assert response.status_code == status.HTTP_303_SEE_OTHER
            
            # Verify the browser is pointed exactly to our login sub-router pathway
            assert response.headers["location"] == "/auth/login"

    def test_unauthorized_redirect_target_exists(self, mock_send, client):
        """
        Verifies that the target redirect location (/auth/login) 
        actually resolves with a successful 200 OK rendering.
        """
        response = client.get("/main", follow_redirects=True)
        
        # Following the redirect should successfully deposit the user on the login view
        assert response.status_code == status.HTTP_200_OK
        # Look for a unique keyword inside your login.html template to prove it loaded
        assert "login" in response.text.lower()

    def test_authorized_access_reads_user_data(self, mock_send, client):
        """
        Simulates an authenticated user holding a valid JWT cookie, 
        ensuring they successfully reach the dashboard data.
        """
        # 1. Create a mock user payload matching your security structure
        user_payload = {
            "sub": "architect_partner@herenciapp.com",
            "email": "architect_partner@herenciapp.com",
            "id": 999
        }
        
        # 2. Generate a valid token string using your secure core function
        token = create_access_token(data=user_payload)
        
        # 3. Inject the token into the TestClient's cookies 
        # (Assuming your app reads the token from an HttpOnly cookie named 'access_token')
        client.cookies.set("access_token", token)
        
        # 4. Make the secure request to /main
        response = client.get("/main")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        # Verify that the dashboard template successfully reads and displays the user data
        assert "architect_partner@herenciapp.com" in response.text