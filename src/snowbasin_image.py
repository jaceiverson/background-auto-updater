import datetime as dt
import glob
import logging
import os

import requests
from rich.logging import RichHandler
from rich.traceback import install

install(show_locals=True)

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    handlers=[RichHandler(markup=True)],
)
logger = logging.getLogger("rich")

"""
We like to use rich for logging and for traceback
it provides a nicer output
"""


class SnowbasinImage:
    def __init__(
        self,
        background_directory: str,
        store_previous_images: bool = True,
        image_size: str = "1080",
    ) -> None:
        """
        initialize the class
        background_directory: the directory where the images will be saved.
         - This is an absolute path.
        Example for Mac: ~/Desktop/backgrounds/
        """
        self.background_file_path: str = background_directory
        self.store_previous_images: bool = store_previous_images
        self.base_url: str = "https://storage.googleapis.com/prism-cam-00054"
        self.image_size: str = image_size
        self.current_image_date: dt.date | None = None
        self.validate_background_directory()
        self.check_directory_structure()

    def set_image_size(self, image_size: str) -> None:
        """
        set the image size
        """
        self.image_size = image_size

    def validate_background_directory(self) -> None:
        """
        validate the background directory added a / to the end if it doesn't exist
        """
        if self.background_file_path[-1] != "/":
            logger.info(f"[yellow]Adding / to the end of the background directory: {self.background_file_path}")
            self.background_file_path = self.background_file_path + "/"

    def check_directory_structure(self) -> None:
        """
        checks the directory structure or `old_backgrounds` and creates a few files if needed
        """
        if self.store_previous_images:
            os.makedirs(os.path.expanduser(f"{self.background_file_path}old_backgrounds/"), exist_ok=True)

    def process(self) -> bool:
        """
        main process for finding and saving the most recent image
        """
        # step 1
        # pull in the current contents of the directory
        current_background_file = self.get_files_in_directory()
        logger.info(f"[blue]Current background image: {current_background_file}")
        # if we have a file, we will convert it (a string) to a datetime object
        if current_background_file:
            # convert to a datetime object
            current_background_image_date = self.make_date_from_file_string(current_background_file.split("/")[-1])
            # step 2-a
            # check the date time
            next_image_to_pull = self.find_next_image_time(current_background_image_date)

        # if we don't find a file, we need to start the process from scratch
        else:
            logger.info("[yellow]No image found in the directory")
            current_background_image_date = ""
            # step 2-b
            # i chose to go back 1 day to find the next image (this is overkill)
            # as long as we went back further than 5 minutes it would get us an image to pull
            next_image_to_pull = self.find_next_image_time(dt.datetime.now() - dt.timedelta(days=1))

        # log the current and next image time
        logger.info(f"Current image time: {current_background_image_date}")
        logger.info(f"Next image time: {next_image_to_pull}")

        # check if the image already exists, we will log and exit the function
        # add a check first to make sure current_background_image_date is not None
        if current_background_image_date and next_image_to_pull.replace(
            second=0, microsecond=0
        ) == current_background_image_date.replace(second=0, microsecond=0):
            logger.info(f"[yellow]Image already exists: {current_background_file}")
            return True

        # step 3
        # get the image and save it
        # if we don't find an image, we will return False and exit the function
        if self.get_image(next_image_to_pull):
            # depending on the value of store_previous_images, we will either move or delete the file
            if self.store_previous_images:
                # if the file doesn't exist, we don't need to move anything
                # this should only happen on the first run
                if current_background_file:
                    # step 4-a
                    # move the file
                    self.move_last_image(current_background_file)
                    logger.info(f"[yellow]Moved {os.path.basename(current_background_file)} to archive folder.")
                # log if there wasn't a file to move
                logger.info(f"[yellow]No previous image to move.")
            else:
                # step 4-b
                # delete the file
                self.delete_file(current_background_file)
                logger.info(f"[yellow]Deleted {os.path.basename(current_background_file)}")
        else:
            return False

    def get_files_in_directory(self) -> str:
        """
        Step 1
        returns the current file in the backgrounds folder
        if there is more than 1 file, it will raise an error
        """
        # Use glob to get a list of files in the directory matching the pattern
        files = glob.glob(os.path.join(os.path.expanduser(self.background_file_path), "*.jpg"))
        if len(files) > 1:
            logger.error(f"[red]More than one file in the directory: {files}")
            raise OSError("More than one file in the directory")
        if files:
            self.current_image_date = self.make_date_from_file_string(files[0].split("/")[-1])
            return files[0]
        else:
            return ""

    @staticmethod
    def make_date_from_file_string(file_name: str) -> dt.datetime:
        """
        helper: make a date from the file name
        """
        return dt.datetime.strptime(file_name, "%Y-%m-%d-%H-%M.jpg")

    @staticmethod
    def find_next_image_time(current_background: dt.datetime) -> dt.datetime:
        """
        Step 2
        return the next good image time as datetime to look for
        """
        right_now = dt.datetime.now()

        # between 8am and 6pm we will look for images every 5 minutes
        if right_now.hour >= 8 and right_now.hour <= 18:
            # if at least 5 minutes haven't passed, return the current background
            # this will skip looking for new images
            if right_now - current_background < dt.timedelta(minutes=5):
                logger.info(
                    "[yellow]Not enough time has passed (5 min). Time difference: "
                    f"{right_now.replace(microsecond=0) - current_background.replace(microsecond=0)}"
                )
                return current_background
            right_now = right_now.replace(minute=right_now.minute // 5 * 5)

        # outside of 8am and 6pm we will look for images every 15 minutes
        else:
            # if at least 15 minutes haven't passed, return the current background
            # this will skip looking for new images
            if right_now - current_background < dt.timedelta(minutes=10):
                logger.info(
                    "[yellow]Not enough time has passed (15 min). Time difference: "
                    f"{right_now.replace(microsecond=0) - current_background.replace(microsecond=0)}"
                )
                return current_background
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
        # return the datetime object without seconds or microseconds
        return right_now.replace(second=0, microsecond=0)

    def get_image(self, image_time_to_pull: dt.date) -> bool:
        """
        Step 3
        scrape Snowbasin image and save to my computer
        return True if successful, False if not
        """
        resp, image_time = self.check_for_non_round_image_times(image_time_to_pull)
        # if we get a good response, we will save the image
        if resp and image_time:
            img_data = resp.content
            file_path = self.make_file_path_string(image_time)
            # make the directory if it doesn't exist
            os.makedirs(os.path.expanduser(self.background_file_path), exist_ok=True)
            # save the image data to the .jpg file
            with open(os.path.expanduser(file_path), "wb") as handler:
                handler.write(img_data)
            logger.info(f"[green]Image downloaded and saved to: {file_path}")
            self.last_image_saved = file_path
            return True
        elif self.current_image_date is None:
            return self.get_image(image_time_to_pull - dt.timedelta(minutes=5))
        else:
            return False

    def check_for_non_round_image_times(
        self, image_time_to_pull: dt.date, request_limit: int = 0
    ) -> tuple[requests.Response | None, dt.date | None]:
        """
        Step 3 helper

        check for non round image times
        if we don't find an image it will look for the previous 4 minute intervals before it
        for example:
        if we are looking for
        2021-09-10 10:15:00

        and we don't find it
        it will look for

        2021-09-10 10:14:00
        then 2021-09-10 10:13:00
        then 2021-09-10 10:12:00
        then 2021-09-10 10:11:00

        if we don't find any of those, it will just return the resp object which will be a 404
        log the result, and don't save a picture
        """
        if (
            image_time_to_pull
            and self.current_image_date
            and image_time_to_pull.replace(second=0, microsecond=0)
            == self.current_image_date.replace(second=0, microsecond=0)
        ):
            logger.info(f"[yellow]Stopping image search, image already exists: {self.current_image_date}")
            return None, None
        # set the URL from the image time
        url = self.make_url_string(image_time_to_pull)
        logger.info(f"[blue]Checking for image at: {url}")
        # make the request for the image
        resp = self.pull_image_from_web(url)
        # if we get a good response, we will return it
        if resp.ok:
            logger.info(f"[green]Image found at: {url}")
            return resp, image_time_to_pull
        # if we get a 404, we will try again with the previous minute
        else:
            logger.info(f"[yellow]Image not found at [/]{url}")
            # if we have tried 5 times, we will return the response
            if request_limit == 4:
                logger.warn("[red]No image found in 5 tries")
                return resp, None
            request_limit += 1
            image_time_to_pull = image_time_to_pull - dt.timedelta(minutes=1)
            return self.check_for_non_round_image_times(image_time_to_pull, request_limit)

    def move_last_image(self, old_file_path: str) -> None:
        """
        Step 4-a
        move the older image file to the archive folder
        """
        old_file_name = os.path.basename(old_file_path)
        new_backgrounds_path = os.path.expanduser(f"{self.background_file_path}old_backgrounds/")
        # check if the directory exists
        if not os.path.exists(new_backgrounds_path):
            logger.info(f"[blue]File not found: {new_backgrounds_path}. Creating directories and file.")
            os.makedirs(new_backgrounds_path, exist_ok=True)
        if not os.path.exists(old_file_path):
            logger.info(f"[blue]File not found: {old_file_path}. Creating directories and file.")
            os.makedirs(old_file_path, exist_ok=True)
        # set the new file path
        new_file_path = os.path.join(new_backgrounds_path, old_file_name)
        # move the file
        os.rename(old_file_path, new_file_path)

    @staticmethod
    def delete_file(old_file_path: str) -> None:
        """
        Step 4-b
        delete file at the given path
        """
        os.remove(old_file_path)

    def make_file_path_string(self, date: dt.datetime, full_path: bool = True) -> str:
        """
        helper function
        make the file path string
        """
        if full_path:
            return (
                f"{self.background_file_path}"
                f"{date.strftime('%Y')}-"
                f"{date.strftime('%m')}-"
                f"{date.strftime('%d')}-"
                f"{date.strftime('%H')}-"
                f"{date.strftime('%M')}.jpg"
            )
        return (
            f"{date.strftime('%Y')}-"
            f"{date.strftime('%m')}-"
            f"{date.strftime('%d')}-"
            f"{date.strftime('%H')}-"
            f"{date.strftime('%M')}.jpg"
        )

    def make_url_string(self, date: dt.datetime) -> str:
        """
        helper function
        make the url string
        """
        return (
            f"{self.base_url}/"
            f"{date.strftime('%Y')}/"
            f"{date.strftime('%m')}/"
            f"{date.strftime('%d')}/"
            f"{date.strftime('%H')}-"
            f"{date.strftime('%M')}/"
            f"{self.image_size}.jpg"
        )

    @staticmethod
    def pull_image_from_web(image_url: str) -> requests.Response:
        """
        helper function
        pull an image from the web
        """
        return requests.get(image_url, timeout=5)

    @staticmethod
    def parse_date_values(date: dt.datetime) -> tuple[str]:
        """
        helper function
        parse the date values into string values return as tuple
        """
        return (
            date.strftime("%Y"),
            date.strftime("%m"),
            date.strftime("%d"),
            date.strftime("%H"),
            date.strftime("%M"),
        )
