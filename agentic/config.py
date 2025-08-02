from pathlib import Path
from pydantic import BaseModel, ValidationError
import yaml


class Settings(BaseModel):
    database_url: str
    ollama_url: str
    ollama_model: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    # azure_openai_embedding_deployment: str
    azure_openai_chat_deployment: str
    azure_openai_api_version: str
    redis_url: str


class Config:
    _settings = None

    @classmethod
    def load(cls, path: str = "config.yaml"):
        if cls._settings is None:
            config_path = Path(path)
            if not config_path.exists():
                raise FileNotFoundError(f"{path} not found")
            with open(config_path, "r") as f:
                raw_cfg = yaml.safe_load(f)
            try:
                cls._settings = Settings(**raw_cfg)
            except ValidationError as e:
                raise RuntimeError(f"Invalid config: {e}")
        return cls._settings

    @classmethod
    def get(cls, key: str, default=None):
        settings = cls.load()
        return getattr(settings, key, default)
