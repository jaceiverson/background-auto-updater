import time
import argparse

from snowbasin_image import SnowbasinImage, logger


def once():
    s = SnowbasinImage("~/Desktop/backgrounds/")
    s.process()


def constant(minute_interval: int = 5):
    try:
        s = SnowbasinImage("~/Desktop/backgrounds/")
        while True:
            s.process()
            time.sleep(60 * minute_interval)
    except KeyboardInterrupt:
        logger.info("[red]Script killed from keyboard interrupt. Exiting...")
        exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Flags to help run this once or constantly"
    )
    parser.add_argument("-c", "--constant", action="store_true", help="run constantly")
    parser.add_argument(
        "-m",
        "--minute-interval",
        type=int,
        default=5,
        help="how often to check for new images in minutes",
    )
    args = parser.parse_args()
    logger.info(f"Running with args: {args}")
    if args.constant:
        constant(args.minute_interval)
    else:
        once()


if __name__ == "__main__":
    main()
