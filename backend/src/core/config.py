from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )
    deepseek_api_key: str | None = None
    openai_api_key: str | None = None
    replicate_api_token: str | None = None
    output_dir: str = "data/outputs"
    checkpoint_db_path: str = "data/checkpoints.db"
    log_level: str = "INFO"
    default_user_id: str = "user_default"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    deepseek_timeout: float = 60.0
    deepseek_temperature: float = 0.2
    langfuse_enabled: bool = False
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()