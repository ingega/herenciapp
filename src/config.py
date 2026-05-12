from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Restaurant Metadata
    APP_NAME: str = "Herenciapp"
    RESTAURANT_NAME: str = "Herencia del Abuelo"
    RESTAURANT_ADDRESS: str = "Plaza San Isidro, local D17, Zapopan, Jalisco"
    RESTAURANT_PHONE: str = "+523334816129"
    RESTAURANT_LOGO_NAME: str = "main_logo.png"
    SHOW_LOGO: bool = True
    
    # Environment config
    DEBUG: bool = True

    # Email Configurations
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Herencia del Abuelo"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    ## Database Configurations

    # App Mode: 'production' or 'mock'
    APP_MODE: str = "mock"

    # Real Database Vars
    DB_HOST: str | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None

    # Mock Database Vars
    MOCK_DB_HOST: str | None = None
    MOCK_DB_NAME: str | None = None
    MOCK_DB_USER: str | None = None
    MOCK_DB_PASSWORD: str | None = None

    ## Pydantic V2+
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields in .env to prevent errors
    )

    @property
    def DATABASE_URL(self) -> str:
        """Dynamically builds the connection string based on APP_MODE"""
        if self.APP_MODE == "production":
            return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}"
        # Default to mock for safety
        return f"postgresql://{self.MOCK_DB_USER}:{self.MOCK_DB_PASSWORD}@{self.MOCK_DB_HOST}/{self.MOCK_DB_NAME}"

@lru_cache()
def get_settings():
    return Settings()

# For convenience, we can also create a global instance of settings
settings = get_settings()