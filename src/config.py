from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Restaurant Metadata
    APP_NAME: str = "Herenciapp"
    RESTAURANT_NAME: str = "Herencia del Abuelo"
    RESTAURANT_ADDRESS: str = "Plaza San Isidro, local D17"
    RESTAURANT_PHONE: str = "+52-33-34-81-61-29"

    # media configuration
    RESTAURANT_LOGO_NAME: str = "main_logo.png"  # Default name
    SHOW_LOGO: bool = True
    
    # Environment config
    DEBUG: bool = True

    class Config:
        env_file = ".env" # This allows to override these via a .env file

settings = Settings()