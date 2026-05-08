# src/api/v1/apps/users/email_service.py
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from src.config import get_settings

settings = get_settings()

# Production-grade SMTP configuration
conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com", # Or your preferred provider
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

async def send_verification_email(email_to: EmailStr, code: str):
    """
    Sends a professional verification email to the user.
    """
    html = f"""
    <h3>Bienvenido a carnitas Herencia del Abuelo!</h3>
    <p>POr favor ingrese el siguiente código para verificar su cuenta:</p>
    <h2 style="color: #d9534f;">{code}</h2>
    <p>Este código expirará en 15 minutos.</p>
    """
    
    message = MessageSchema(
        subject="Herenciapp - Verificación de Correo",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
