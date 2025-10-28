from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    # JWT settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
settings = Settings()