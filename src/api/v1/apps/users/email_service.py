# src/api/v1/apps/users/email_service.py
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from src.config import get_settings

def get_mail_client() -> FastMail:
    """
    Initializes the mail client only when called.
    This prevents errors during test collection if env vars are missing.
    """
    settings = get_settings()
    conf = ConnectionConfig(
        MAIL_USERNAME = settings.MAIL_USERNAME,
        MAIL_PASSWORD = settings.MAIL_PASSWORD,
        MAIL_FROM = settings.MAIL_FROM,
        MAIL_PORT = 587,
        MAIL_SERVER = "smtp.gmail.com",
        MAIL_STARTTLS = True,
        MAIL_SSL_TLS = False,
        USE_CREDENTIALS = True
    )
    return FastMail(conf)

async def send_verification_email(email_to: str, code: str):
    html = f"<h3>Code: {code}</h3>"
    message = MessageSchema(
        subject="Herenciapp - Verify",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
    
    # We call our helper here
    fm = get_mail_client()
    await fm.send_message(message)