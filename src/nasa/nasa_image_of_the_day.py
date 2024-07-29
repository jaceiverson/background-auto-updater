import requests
from bs4 import BeautifulSoup
from core.background import BackgroundImageFetcher
from core.logger import logger


def get_main_page():
    url = "https://www.nasa.gov/image-of-the-day/"
    return requests.get(url, timeout=10)


def find_most_recent_image(soup: BeautifulSoup):
    return soup.find("div", {"class": "hds-gallery-items"}).find("img")["src"]


def main():
    # scrape nasa to get the most recent image
    response = get_main_page()
    soup = BeautifulSoup(response.content, "html.parser")
    image_url = find_most_recent_image(soup)
    # process the image and save it to the file
    nasa = BackgroundImageFetcher()
    nasa.process(image_url)


if __name__ == "__main__":
    main()
