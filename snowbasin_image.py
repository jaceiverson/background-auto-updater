#!/venv/bin/python3
import os
import datetime as dt
import logging
import glob
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


class SnowbasinImage:
    def __init__(
        self,
        background_directory: str,
        store_previous_images: bool = True,
        image_size: str = "1080",
    ) -> None:
        """
        initialize the class
        background_directory: the directory where the images will be saved. This is an absolute path.
        Example ~/Desktop/backgrounds/
        """
        self.background_file_path = background_directory
        self.store_previous_images = store_previous_images
        self.base_url = "https://storage.googleapis.com/prism-cam-00054"
        self.image_size = image_size

    def set_image_size(self, image_size: str) -> None:
        """
        set the image size
        """
        self.image_size = image_size

    def make_url_string(self, date: dt.datetime) -> str:
        """
        make the url string
        """
        return f"{self.base_url}/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}/{date.strftime('%H')}-{date.strftime('%M')}/{self.image_size}.jpg"

    def make_file_path_string(self, date: dt.datetime, full_path: bool = True) -> str:
        """
        make the file path string
        """
        if full_path:
            return f"{self.background_file_path}{date.strftime('%Y')}-{date.strftime('%m')}-{date.strftime('%d')}-{date.strftime('%H')}-{date.strftime('%M')}.jpg"
        return f"{date.strftime('%Y')}-{date.strftime('%m')}-{date.strftime('%d')}-{date.strftime('%H')}-{date.strftime('%M')}.jpg"

    @staticmethod
    def make_date_from_file_string(file_name: str) -> dt.datetime:
        """
        make a date from the file name
        """
        return dt.datetime.strptime(file_name, "%Y-%m-%d-%H-%M.jpg")

    def check_for_non_round_image_times(
        self, image_time_to_pull: dt.date, request_limit: int = 0
    ) -> requests.models.Response:
        """
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
        url = self.make_url_string(image_time_to_pull)
        logger.info(f"[blue]Checking for image at: {url}")
        resp = requests.get(url)
        if resp.ok:
            logger.info(f"[green]Image found at: {url}")
            return resp, image_time_to_pull
        else:
            logger.info(f"[yellow]Image not found at [/]{url}")
            if request_limit == 5:
                logger.warn("[red]No image found in 5 tries")
                return resp
            request_limit += 1
            image_time_to_pull = image_time_to_pull - dt.timedelta(
                minutes=request_limit
            )
            return self.check_for_non_round_image_times(
                image_time_to_pull, request_limit
            )

    def get_image(self, image_time_to_pull: dt.date) -> bool:
        """
        scrape Snowbasin image and save to my computer
        return True if successful, False if not
        """
        resp, image_time = self.check_for_non_round_image_times(image_time_to_pull)
        # if we get a good response, we will save the image
        if resp.ok:
            img_data = resp.content
            file_path = self.make_file_path_string(image_time)
            with open(os.path.expanduser(file_path), "wb") as handler:
                handler.write(img_data)
            logger.info(f"[green]Image downloaded and saved to: {file_path}")
            return True
        else:
            return False

    @staticmethod
    def find_next_image_time(current_background: dt.datetime) -> dt.datetime:
        """
        return the next good image time as datetime to look for
        """
        right_now = dt.datetime.now()
        if right_now - current_background < dt.timedelta(minutes=5):
            # if at least 6 minutes haven't passed, return the current background
            # this will skip looking for new images
            return current_background

        if right_now.hour >= 8 and right_now.hour <= 18:
            # between 8am and 6pm we will look for images every 5 minutes
            right_now = right_now.replace(minute=right_now.minute // 5 * 5)
        else:
            # outside of 8am and 6pm we will look for images every 15 minutes
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
        return right_now

    @staticmethod
    def parse_date_values(date: dt.datetime) -> tuple[str]:
        """
        parse the date values into string values return as tuple
        """
        return (
            date.strftime("%Y"),
            date.strftime("%m"),
            date.strftime("%d"),
            date.strftime("%H"),
            date.strftime("%M"),
        )

    def get_files_in_directory(self) -> str:
        """
        returns the current file in the backgrounds folder
        if there is more than 1 file, it will raise an error
        """
        try:
            # Use glob to get a list of files in the directory matching the pattern
            files = glob.glob(
                os.path.join(os.path.expanduser(self.background_file_path), "*.jpg")
            )
            if len(files) > 1:
                raise OSError("More than one file in the directory")
            return files[0]
            # Print the list of files
        except OSError as e:
            logger.error(f"Error: {e}")

    def move_last_image(self, old_file_path: str):
        """
        move the older image file to the archive folder
        """
        old_file_name = os.path.basename(old_file_path)
        new_backgrounds_path = os.path.expanduser(
            f"{self.background_file_path}old_backgrounds/"
        )
        # check if the directory exists
        if not os.path.exists(new_backgrounds_path):
            os.makedirs(new_backgrounds_path)
        # set the new file path
        new_file_path = os.path.join(new_backgrounds_path, old_file_name)
        # move the file
        os.rename(old_file_path, new_file_path)

    @staticmethod
    def delete_file(old_file_path: str):
        """
        delete file at the given path
        """
        os.remove(old_file_path)

    def process(self):
        """
        main process for looking for the right time
        pulling image
        and moving/deleting the old image
        """
        # pull in the current contents of the directory
        current_background_file = self.get_files_in_directory()
        logger.info(f"[blue]Current background image: {current_background_file}")
        # convert to a datetime object
        current_background_image_date = self.make_date_from_file_string(
            current_background_file.split("/")[-1]
        )
        # check the date time
        next_image_to_pull = self.find_next_image_time(current_background_image_date)
        # check if the image already exists, we will log and exit the function
        if next_image_to_pull == current_background_image_date:
            logger.info(
                f"[yellow]Not enough time has passed (5 min). Image already exists: {current_background_file}"
            )
            return True
        # get the image
        if self.get_image(next_image_to_pull):
            # depending on the value of store_previous_images, we will either move or delete the file
            if self.store_previous_images:
                # move the file
                self.move_last_image(current_background_file)
                logger.info(
                    f"[yellow]Moved {os.path.basename(current_background_file)} to archive folder."
                )
            else:
                # delete the file
                self.delete_file(current_background_file)
                logger.info(
                    f"[yellow]Deleted {os.path.basename(current_background_file)}"
                )
        else:
            return False


if __name__ == "__main__":
    s = SnowbasinImage("~/Desktop/backgrounds/")
    s.process()
