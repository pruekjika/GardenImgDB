#python3
# from [How do I get time of a Python program's execution? - Stack Overflow](https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution)
import atexit
from time import time, strftime, localtime
from datetime import timedelta
from log_setup import logger

def secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%d-%b-%Y %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))

def log(s, elapsed=None):
    line = "="*40
    logger.info(line)
    word = f"{secondsToStr()} {'-'} {s}"
    logger.info(word)
    if elapsed:
        logger.info(f"Elapsed time: {elapsed}")
    logger.info(line)

def endlog():
    end = time()
    elapsed = end-start
    log("End Program", secondsToStr(elapsed))
    

start = time()
atexit.register(endlog)
log("Start Program")
