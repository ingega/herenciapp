from unittest.mock import AsyncMock, patch
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, get_session

# prepare in-memory engine and create tables
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(engine)

# override dependency
def get_session_override():
    with Session(engine) as s:
        yield s

app.dependency_overrides[get_db] = get_session_override
app.dependency_overrides[get_session] = get_session_override

with patch('src.api.v1.apps.users.email_service.FastMail.send_message', new_callable=AsyncMock) as mock_send:
    with TestClient(app) as client:
        user_data = {"email":"patchtest@herenciapp.com", "password":"Password123!"}
        r = client.post('/users/register', json=user_data)
        print('register status', r.status_code, r.text)
        print('mock_send called?', mock_send.called)
        # inspect tokens
        r2 = client.post('/users/verify', json={'email': user_data['email'], 'token': '000000'})
        print('verify with wrong token status', r2.status_code)
