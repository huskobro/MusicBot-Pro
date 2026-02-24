import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("TestLogger")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("logs/musicbot.log", maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Test log entry")
print("Logs integrated!")
