from pathlib import Path
from typing import List
from pydantic import BaseModel
import tomli
import yaml


class ServerConfig(BaseModel):
    """Configuration for the FastAPI server."""

    host: str
    port: int
    api_key: str
    reload: bool


class LoggingConfig(BaseModel):
    """Configuration for application logging."""

    log_level: str
    log_to_file: bool
    log_file_path: str
    colorize: bool
    enqueue: bool
    backtrace: bool
    diagnose: bool
    rotation: str
    retention: str


class DBConfig(BaseModel):
    database_url: str
    redis_url: str


class OllamaSettings(BaseModel):
    embedding_url: str
    embedder_model: str


class AzureSettings(BaseModel):
    endpoint: str
    api_key: str
    chat_deployment: str
    api_version: str


class OpenAISettings(BaseModel):
    api_key: str


class SplitterSettings(BaseModel):
    chunk_size: int
    chunk_overlap: int
    language: str


class LLMConfig(BaseModel):
    """LLM config now includes temperature and timeout."""

    retriever_top_k: int
    embedding_dim: int
    temperature: float
    request_timeout: float
    ollama: OllamaSettings
    azure: AzureSettings
    openai: OpenAISettings


class RAGAgentConfig(BaseModel):
    """RAG config now includes ignore patterns for the ingestor."""

    system_prompt: str
    model: str
    ingestor_ignore_patterns: List[str]


class AppConfig(BaseModel):
    """The root configuration model, now including server and logging."""

    server: ServerConfig
    logging: LoggingConfig
    db: DBConfig
    llm: LLMConfig
    rag: RAGAgentConfig
    splitter: SplitterSettings


# --- Configuration Loader ---


def get_config() -> AppConfig:
    """
    Loads configuration from 'config/config.toml' or 'config/config.yaml'.
    It prioritizes the .toml file if both exist.
    """
    project_root = Path(__file__).parent.parent.parent
    config_dir = project_root / "config"
    toml_path = config_dir / "config.toml"
    yaml_path = config_dir / "config.yaml"

    config_data = None

    if toml_path.exists():
        print(f"Loading configuration from {toml_path}")
        with open(toml_path, "rb") as f:
            config_data = tomli.load(f)
    elif yaml_path.exists():
        print(f"Loading configuration from {yaml_path}")
        with open(yaml_path, "r") as f:
            config_data = yaml.safe_load(f)
    else:
        raise FileNotFoundError(
            f"Configuration file not found. Please create 'config.toml' or 'config.yaml' in the '{config_dir}' directory."
        )

    return AppConfig(**config_data)


config = get_config()
