# Snowbasin Live Background

<img width="1010" alt="Snowbasin Mt Ogden webcam" src="https://github.com/jaceiverson/snowbasin-background-auto-updater/assets/47643209/0851141a-537c-4416-8b85-bcfec7935f33">

Pulled from Mt. Ogden webcam: https://www.snowbasin.com/the-mountain/web-cams/

This image is taken every 5 minutes during the day (8am to 6pm) and around every 15 minutes during the evening (6pm to 8am). These images are saved at a googleapi endpoint: https://storage.googleapis.com/prism-cam-00054/ and can be retrieved with altering the date code in the URL. We found this from the inspect tool in chrome:

<img width="1680" alt="Mt Ogden webcam - inspect view" src="https://github.com/jaceiverson/snowbasin-background-auto-updater/assets/47643209/b7b9a72a-5e91-4697-b2d6-f1b2147e0806">

I wanted to create a program that allows me to change the background to the most recent image.

## Command Line Script

You can run the script as a one off or have it run as often as you'd like. You will need to install the local module for the shorthand script to work:

```
pip install -e .
```

Then you will be able to use the alias in the terminal:

```
check-sb
```

If you run it using the script and not as a cronjob/scheduled job, it is recommended to use a screen to run it in the background.

### Flags

The main flag that should be used is `-f`. This tells the program which directory to save and look for files in. The default file path is:

```
~/Desktop/backgrounds/
```

There is a flag `-c` or `--constant` that you can use to check forever (until you kill the program). There is also another flag `-m` or `--minute` that will tell the program how frequently--in minutes--to check for a new image (default is 5).

## Auto Updating Background

### MAC

Online there are some solutions for using an os script to alter the background, but I couldn't get any of those to work. So I came up with my own solution. I have a designated `backgrounds` directory on my desktop. On my Mac I set the background images to shuffle through the images in this folder. Every 5 minutes my script runs trying to pull a new image. If we find a new one, we move the current image into a sub-directory and then save the new one in. I set the backgrounds to change every 5 seconds so as soon as a new one comes in, it is updated.
