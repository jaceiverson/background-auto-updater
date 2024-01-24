import datetime as dt
import requests


def find_good_times(year: str, month: str, day: str):
    """
    used for testing, scraped all 5 minute intervals for a given day
    saved the results to a dictionary
    used it to determine how often the site updates their image
    every 5 minutes from 8am to 6pm
    every 15 minutes from 6pm to 8am
    """
    results = {}
    for x in range(0, 24):
        for y in range(0, 60, 5):
            hour = str(x).zfill(2)
            minute = str(y).zfill(2)
            image_size = "1080"
            url = f"https://storage.googleapis.com/prism-cam-00054/{year}/{month}/{day}/{hour}-{minute}/{image_size}.jpg"
            resp = requests.get(url)
            results[f"{hour}:{minute}"] = resp.status_code
    return results


def check_date_time() -> tuple:
    """
    old function to return string formated date, replaced with find_last_good_time
    """
    # get the current date
    right_now = dt.datetime.now()
    if right_now.hour >= 8 and right_now.hour <= 18:
        if right_now.minute in range(0, 60, 5):
            return (
                right_now.strftime("%Y"),
                right_now.strftime("%m"),
                right_now.strftime("%d"),
                right_now.strftime("%H"),
                right_now.strftime("%M"),
            )
    else:
        if right_now.minute in [5, 20, 35, 50]:
            return (
                right_now.strftime("%Y"),
                right_now.strftime("%m"),
                right_now.strftime("%d"),
                right_now.strftime("%H"),
                right_now.strftime("%M"),
            )
    return False
