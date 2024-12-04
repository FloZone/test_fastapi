from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    model_config = SettingsConfigDict(env_file="../.env")


def get_settings() -> Settings:
    return Settings()