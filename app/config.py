from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_driver: str = Field(default="postgress", min_length=4)
    database_hostname: str = Field(default="localhost", min_length=1)
    database_port: int = Field(default=5432, ge=1024, le=65535)
    database_name: str = Field(default="fastapi", min_length=2)

    database_username: str = Field(default="username", min_length=1)
    database_password: str = Field(default="password", min_length=4)

    secret_key: str = Field(default="secret", min_length=4)
    algorithm: str = Field(default="HS256", min_length=4)
    access_token_expire_minutes: int = Field(default=30, gt=0)


settings = Settings()
