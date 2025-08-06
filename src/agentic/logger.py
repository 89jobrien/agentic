# agentic/logging_setup.py
import sys
from loguru import logger
from src.agentic.config import LoggingConfig
from src.agentic.formatting.console import get_rich_handler


def setup_logging(log_config: LoggingConfig):
    """Configures the application's logger based on config settings."""
    logger.remove()  # Remove the default handler

    # Use our custom RichHandler for all console output
    logger.add(
        get_rich_handler(),
        level=log_config.log_level.upper(),
        format="{message}", # RichHandler handles its own formatting
    )

    # Add a handler for file output if enabled
    if log_config.log_to_file:
        logger.add(
            log_config.log_file_path,
            level=log_config.log_level.upper(),
            rotation=log_config.rotation,
            retention=log_config.retention,
            enqueue=log_config.enqueue,
            backtrace=log_config.backtrace,
            diagnose=log_config.diagnose,
        )
