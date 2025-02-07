from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_PATH: str = "/api"
    API_V1_PATH: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file="../.env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
