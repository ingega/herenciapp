import os
os.environ.setdefault('MAIL_USERNAME','test')
os.environ.setdefault('MAIL_PASSWORD','test')
os.environ.setdefault('MAIL_FROM','test@local')

import asyncio
from unittest.mock import AsyncMock, patch
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from src.api.v1.apps.users.services import create_pending_user
from src.api.v1.apps.users.schemas import UserCreate

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(engine)

async def run():
    with Session(engine) as s:
        user_in = UserCreate(email="debug2@herenciapp.com", password="Secret123!")
        with patch('src.api.v1.apps.users.email_service.FastMail.send_message', new_callable=AsyncMock) as mock_send:
            user = await create_pending_user(s, user_in)
            print('created user:', user)
            print('mock_send called:', mock_send.called)

asyncio.run(run())
