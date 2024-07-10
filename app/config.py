from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_driver: str = "postgress"
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_name: str = "fastapi"

    database_username: str = ""
    database_password: str = ""

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
