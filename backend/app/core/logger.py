# Imports dependencies.
import os
import sys
from loguru import logger

# Automatically resolve the backend/logs directory.
LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "caso_rag_{time:YYYY-MM-DD}.log")

# Reset default handler to avoid duplicate logs.
logger.remove()

# 1. Console Output (colored & readable for terminal)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 2. File Sink (persistent, detailed DEBUG logs, automatic 10MB rotation, 14-day retention)
logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="14 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}: {line} - {message}",
    encoding="utf-8"
)

logger.info(f"Persistent logging initialized. Writing logs to: {LOG_DIR}")