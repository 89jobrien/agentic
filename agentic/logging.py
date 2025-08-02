from loguru import logger
import sys
def setup_logging():
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time} | {level} | {name} | {message}")
    logger.add("agentic.log", level="INFO", rotation="1 week", compression="zip")
