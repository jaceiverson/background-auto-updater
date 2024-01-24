#!/venv/bin/python3
import os
import datetime as dt
import logging
import glob
import requests
from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    handlers=[RichHandler(markup=True)],
)
logger = logging.getLogger("rich")


def get_image(url: str, file_path: str) -> bool:
    """
    scrape Snowbasin image and save to my computer
    return True if successful, False if not
    """
    resp = requests.get(url)
    if resp.ok:
        img_data = resp.content
        with open(file_path, "wb") as handler:
            handler.write(img_data)
        logger.info(f"Image downloaded and saved to [yellow]{file_path}")
        return True
    else:
        return False


def move_last_image(old_file_path: str):
    """
    move the older file to the archive folder
    """
    old_file_name = os.path.basename(old_file_path)
    new_backgrounds_path = os.path.expanduser("~/Desktop/backgrounds/old_backgrounds/")
    new_file_path = os.path.join(new_backgrounds_path, old_file_name)
    os.rename(old_file_path, new_file_path)


def find_last_image_time() -> tuple:
    """
    return the last good image time
    formatted as a tuple
    (year, month, day, hour, minute)
    """
    right_now = dt.datetime.now()
    if right_now.hour >= 8 and right_now.hour <= 18:
        right_now = right_now.replace(minute=right_now.minute // 5 * 5)
    else:
        if right_now.minute < 5:
            right_now = right_now.replace(minute=50)
            right_now = right_now - dt.timedelta(hours=1)
        elif right_now.minute < 20:
            right_now = right_now.replace(minute=5)
        elif right_now.minute < 35:
            right_now = right_now.replace(minute=20)
        elif right_now.minute < 50:
            right_now = right_now.replace(minute=35)
        elif right_now.minute < 60:
            right_now = right_now.replace(minute=50)
    return (
        right_now.strftime("%Y"),
        right_now.strftime("%m"),
        right_now.strftime("%d"),
        right_now.strftime("%H"),
        right_now.strftime("%M"),
    )


def get_files_in_directory():
    """
    returns all files in the backgrounds folder
    """
    try:
        # Use glob to get a list of files in the directory matching the pattern
        return glob.glob(
            os.path.join(os.path.expanduser("~/Desktop/backgrounds/"), "*.jpg")
        )
        # Print the list of files
    except OSError as e:
        logger.error(f"Error: {e}")


def main():
    # check the date time
    last_image_time = find_last_image_time()
    # unpack the date time
    year, month, day, hour, minute = last_image_time
    # set the file path
    desktop_path = os.path.expanduser("~/Desktop/backgrounds/")
    file_name = f"{year}-{month}-{day}-{hour}-{minute}.jpg"
    # pull in the current contents of the directory
    current_files = get_files_in_directory()
    # check if the file exists there already
    if file_name in current_files[0] or len(current_files) > 1:
        logger.info(f"Image already exists: [yellow]{file_name}")
        return True
    # we will pull a new file
    old_file_name = current_files[0]
    # set the image size
    image_size = "1080"
    # set the base url
    base_url = f"https://storage.googleapis.com/prism-cam-00054/{year}/{month}/{day}/{hour}-{minute}/{image_size}.jpg"
    logger.info(f"Checking for image at [yellow]{base_url}")
    # get the image
    if get_image(base_url, os.path.join(desktop_path, file_name)):
        # move the file
        move_last_image(old_file_name)
        logger.info(f"Moved {os.path.basename(old_file_name)} to archive folder.")
    else:
        logger.info(f"[red]Image not found at [yellow]{base_url}")
        return False


if __name__ == "__main__":
    main()
