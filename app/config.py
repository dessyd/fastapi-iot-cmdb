from pydantic import BaseSettings


class Settings(BaseSettings):
    database_driver: str = "postgresql"
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_name: str = "fastapi"

    database_username: str
    database_password: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
