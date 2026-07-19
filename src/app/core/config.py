from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Astrology App API"
    API_V1_STR: str = "/api/v1"
    
    #postgres://avnadmin:AVNS_hzM6GlflMP7dLONrY9a@pg-34e6ac9e-naveendevarapalli99-9c54.b.aivencloud.com:13847/astroapp?sslmode=require


    POSTGRES_SERVER: str = "pg-34e6ac9e-naveendevarapalli99-9c54.b.aivencloud.com"
    POSTGRES_USER: str = "avnadmin"
    POSTGRES_PASSWORD: str = "AVNS_hzM6GlflMP7dLONrY9a"
    POSTGRES_DB: str = "astroapp"
    POSTGRES_PORT: str = "13847"

    # local Database for testing
    # POSTGRES_SERVER: str = "localhost"
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "password"
    # POSTGRES_DB: str = "astroapp"
    # POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    # Security
    SECRET_KEY: str = "a_very_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 14400
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Razorpay
    RAZORPAY_KEY_ID: str = "rzp_test_TFPKRhkm0JrKAw"
    RAZORPAY_KEY_SECRET: str = "n5ePGtiZ6CMVga71Roe19TGW"

    
    # Agora
    AGORA_APP_ID: str = "placeholder_agora_app_id"
    AGORA_APP_CERTIFICATE: str = "placeholder_agora_app_cert"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
