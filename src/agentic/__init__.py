from agentic.config import config
from agentic.logger import setup_logging

setup_logging(config.logging)

from loguru import logger

logger.info("Logger successfully initialized and configured.")