import datetime as dt
import glob
import os

import requests
from rich.traceback import install
from core.logger import logger

install(show_locals=False)



class PostInitCaller(type):
    # https://stackoverflow.com/questions/795190/how-to-perform-common-post-initialization-tasks-in-inherited-classes
    def __call__(cls, *args, **kwargs):
        # sourcery skip: instance-method-first-arg-name
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj


class BackgroundImageFetcher(metaclass=PostInitCaller):
    def __init__(
        self,
        background_directory: str = None,
        store_previous_images: bool = True,
    ) -> None:
        """
        initialize the class
        background_directory: the directory where the images will be saved.
        store_previous_images: if True, the previous image will be moved to a folder called `old_backgrounds`
         - This is an absolute path.
        Example for Mac: ~/Desktop/backgrounds/
        """
        self.background_file_path: str = background_directory or os.path.expanduser("~/Desktop/backgrounds/")
        self.store_previous_images: bool = store_previous_images
        self.current_image_date: dt.date | None = None

    def __post_init__(self) -> None:
        """
        post init function to run after the class is initialized
        """
        self.validate_background_directory()
        self.check_directory_structure()
        logger.info(f"[yellow]Background directory: {self.background_file_path}")
        logger.info(f"[yellow]Store previous images: {self.store_previous_images}")

    def validate_background_directory(self) -> None:
        """
        validate the background directory added a / to the end if it doesn't exist
        """
        logger.info("[yellow]Validating the background directory...")
        if self.background_file_path[-1] != "/":
            logger.info(f"[yellow]Adding / to the end of the background directory: {self.background_file_path}")
            self.background_file_path = os.path.join(self.background_file_path, "")

    def check_directory_structure(self) -> None:
        """
        checks the directory structure or `old_backgrounds` and creates a few files if needed
        """
        logger.info("[yellow]Checking the directory structure. Will add `old_backgrounds` if needed...")
        if self.store_previous_images:
            os.makedirs(os.path.expanduser(f"{self.background_file_path}old_backgrounds/"), exist_ok=True)

    def process(self, url_to_get: str) -> None:
        """
        main process function
        """
        # Step 1
        current_file = self.get_current_files_in_directory()
        if not current_file:
            logger.info("[yellow]No image found in the directory")
        elif current_file == self.make_file_path_string(dt.date.today()):
            logger.info(f"[yellow]Image already exists: {current_file}")
            return False
        # Step 2
        new_image = self.pull_image_from_web(url_to_get)
        logger.info(f"[blue]Pulled image from the web: {url_to_get}")
        # Step 3
        self.write_image_to_file(new_image, self.make_file_path_string(dt.date.today()))
        logger.info(f"[blue]Wrote image to file: {self.make_file_path_string(dt.date.today())}")
        if current_file:
            if self.store_previous_images:
                self.move_last_image(current_file)
                logger.info(f"[blue]Moved last image to old_backgrounds: {current_file}")
            else:
                self.delete_file(current_file)
                logger.info(f"[blue]Deleted last image: {current_file}")

        return True

    def get_current_files_in_directory(self) -> str:
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

    @staticmethod
    def pull_image_from_web(image_url: str) -> requests.Response:
        """
        helper function
        pull an image from the web
        """
        return requests.get(image_url, timeout=5)

    @staticmethod
    def write_image_to_file(image_response_object: requests.Response, file_path: str) -> None:
        """
        helper function
        write the image to a file
        """
        with open(os.path.expanduser(file_path), "wb") as handler:
            handler.write(image_response_object.content)

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
