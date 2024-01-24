# Snowbasin Live Background

Pulled from Mt. Ogden webcam: https://www.snowbasin.com/the-mountain/web-cams/

This image is taken every 5 minutes during the day (8am to 6pm) and around every 15 minutes during the evening (6pm to 8am). These images are saved at a googleapi endpoint: https://storage.googleapis.com/prism-cam-00054/ and can be retrieved with altering the date code in the URL.

## Auto Updating Background

Online there are some solutions for using an os script to alter the background, but I couldn't get any of those to work. So I came up with my own solution. I have a designated `backgrounds` directory on my desktop. On my Mac I set the background images to shuffle through the images in this folder. Every 5 minutes my script runs trying to pull a new image. If we find a new one, we move the current image into a sub-directory and then save the new one in. I set the backgrounds to change every 5 seconds so as soon as a new one comes in, it is updated.

## crontab

```
*/5 * * * * cd /Users/jiverson/Desktop/snowbasin-backgrounds/ && venv/bin/python snowbasin_image.py >> image.log 2>&1
```
