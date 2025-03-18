#!/venv/bin/python3
import argparse
import datetime as dt
import time

from src.snowbasin.snowbasin_image import SnowbasinImage, logger


def once(folder_path: str) -> None:
    """
    Run the script once and exit
    """
    s = SnowbasinImage(folder_path)
    s.process()


def constant(folder_path: str, minute_interval: int = 5) -> None:
    """
    Run the script constantly and check for new images every minute_interval minutes
    """
    try:
        s = SnowbasinImage(folder_path)
        while True:
            s.process()
            time.sleep(60 * minute_interval)
    except KeyboardInterrupt:
        logger.info("[red]Script killed from keyboard interrupt. Exiting...")
        exit(0)


def one_day(date: str, polling_frequency: int) -> None:
    """
    Attempt to pull images for an entire day

    Args
    ---
    date: str
        date to pull images for in the format YYYY-MM-DD
    polling_frequency: int
        how often to check for new images in seconds
        default is 1 second
    """
    file_path = f"~/Documents/backgrounds/{date}/"
    s = SnowbasinImage(background_directory=file_path)
    # convert string date to datetime
    d = dt.datetime.strptime(date, "%Y-%m-%d")
    result = s.pull_one_day_to_old_backgrounds(d, polling_frequency)
    logger.info(f"We found {result} images for {date}. Saved to {file_path}")


def main() -> None:
    """
    Main function to parse arguments and run the script
    command line accessible through `check-sb`
    None of the flags are required and all have defaults
    """
    parser = argparse.ArgumentParser(description="Snowbasin Image downloader CLI tool.")
    parser.add_argument(
        "-c",
        "--constant",
        action="store_true",
        help="check every -m minutes for a new background",
    )
    parser.add_argument(
        "-m",
        "--minute-interval",
        type=int,
        default=5,
        help="how often to check for new images in minutes",
    )
    parser.add_argument(
        "-f",
        "--folder-path",
        type=str,
        default="~/Desktop/backgrounds/",
        help="folder path to save images to",
    )
    parser.add_argument(
        "-d",
        "--one-day",
        type=str,
        default=None,
        help="pull images for a specific day. format: YYYY-MM-DD",
    )
    parser.add_argument(
        "-s",
        "--polling-frequency-seconds",
        type=int,
        default=1,
        help="used with -d, how often to check for new images in seconds",
    )
    args = parser.parse_args()
    logger.info(f"Running with args: {args}")
    if args.constant and args.one_day:
        logger.error("[red]Cannot run constant (-c) and one_day (-d) at the same time")
        exit(1)
    if args.constant:
        constant(args.folder_path, args.minute_interval)
    elif args.one_day:
        one_day(args.one_day, args.polling_frequency_seconds)
    else:
        once(args.folder_path)


if __name__ == "__main__":
    main()
