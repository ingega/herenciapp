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

    # Pydantic V2+
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()