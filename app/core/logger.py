from loguru import logger
import os
import sys

os.makedirs("logs", exist_ok=True)

logger.remove()
logger.add(sys.stdout, serialize=True)
logger.add("logs/record_sync.log", rotation="10 MB", retention="14 days", serialize=True)
