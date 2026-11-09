import logging
import sys

LOG_FILE = "meangpu.log"

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
