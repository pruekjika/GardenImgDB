# importing module
import logging
import sys

log_path = r"./meangpu.log"

# Create and configure logger
# format='- %(levelName)s %(asctime)s %(message)s'
logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler(sys.stdout)],
)

# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)


def main():
    logger.info("this is a test debug")


if __name__ == "__main__":
    main()
