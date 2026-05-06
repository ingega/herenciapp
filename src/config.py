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

    ## Database Configurations

    # App Mode: 'production' or 'mock'
    APP_MODE: str = "mock"

    # Real Database Vars
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    # Mock Database Vars
    MOCK_DB_HOST: str
    MOCK_DB_NAME: str
    MOCK_DB_USER: str
    MOCK_DB_PASS: str

    ## Pydantic V2+
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def DATABASE_URL(self) -> str:
        """Dynamically builds the connection string based on APP_MODE"""
        if self.APP_MODE == "production":
            return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}"
        # Default to mock for safety
        return f"postgresql://{self.MOCK_DB_USER}:{self.MOCK_DB_PASS}@{self.MOCK_DB_HOST}/{self.MOCK_DB_NAME}"

@lru_cache()
def get_settings():
    return Settings()