"""
I use this running in a screen on my terminal on my mac
to run this I do the following:
1) open a terminal
2) type screen -R snowbasin
3) type python3 forever.py
4) press ctrl-a then ctrl-d to detach from the screen (but keep it running)
"""
from snowbasin_image import SnowbasinImage
from snowbasin_image import logger
import time

if __name__ == "__main__":
    s = SnowbasinImage("~/Desktop/backgrounds/")
    while True:
        logger.info("Checking for new images")
        s.process()
        time.sleep(60 * 5)
