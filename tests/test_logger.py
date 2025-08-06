from src.agentic.logger import setup_logging
from src.agentic.config import LoggingConfig

def test_setup_logging(patch_config):
    log_cfg = LoggingConfig(
        log_level="INFO",
        log_to_file=False,
        log_file_path="test.log",
        colorize=True,
        enqueue=False,
        backtrace=True,
        diagnose=True,
        rotation="1 week",
        retention="4 weeks"
    )
    setup_logging(log_cfg)
