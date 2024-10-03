import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
from noSongImage import noSongImage
import requests
from io import BytesIO
from PIL import Image

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
import sys, os
import configparser


if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configuration file
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, "../config/rgb_options.ini")

    # Configures logger for storing song data
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        filename="spotipy.log",
        level=logging.INFO,
    )
    logger = logging.getLogger("spotipy_logger")

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler("spotipy.log", maxBytes=2000, backupCount=3)
    logger.addHandler(handler)

    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(filename)

    options = RGBMatrixOptions()
    options.rows = int(config["DEFAULT"]["rows"])
    options.cols = int(config["DEFAULT"]["columns"])
    options.chain_length = int(config["DEFAULT"]["chain_length"])
    options.parallel = int(config["DEFAULT"]["parallel"])
    options.hardware_mapping = config["DEFAULT"]["hardware_mapping"]
    options.gpio_slowdown = int(config["DEFAULT"]["gpio_slowdown"])
    options.brightness = int(config["DEFAULT"]["brightness"])
    options.limit_refresh_rate_hz = int(config["DEFAULT"]["refresh_rate"])
    matrix = RGBMatrix(options=options)

    default_image = os.path.join(dir, config["DEFAULT"]["default_image"])
    weather_location = config["DEFAULT"]["weather_location"]
    schedule_start_str = config["DEFAULT"]["schedule_start"] + time.strftime(
        ", %m/%d/%Y", time.localtime()
    )
    schedule_start = time.strptime(schedule_start_str, "%H:%M, %m/%d/%Y")
    schedule_end_str = config["DEFAULT"]["schedule_end"] + time.strftime(
        ", %m/%d/%Y", time.localtime()
    )
    schedule_end = time.strptime(schedule_end_str, "%H:%M, %m/%d/%Y")  # don't judge me

    prevSong = ""
    currentSong = ""
    prevTime = ""
    currentTime = ""
    size = (matrix.width, matrix.height)

    try:
        while True:
            currentTime = time.strftime("%H:%M", time.localtime())
            if schedule_start <= time.localtime() <= schedule_end:
                try:
                    imageURL = getSongInfo(username, token_path)[1]
                    currentSong = imageURL

                    if prevSong != currentSong:
                        response = requests.get(imageURL)
                        image = Image.open(BytesIO(response.content))
                        image.thumbnail(size, Image.LANCZOS)
                        matrix.SetImage(image.convert("RGB"))
                        prevSong = currentSong

                    time.sleep(1)
                except Exception as e:
                    if prevTime != currentTime:
                        matrix.SetImage(
                            noSongImage(size, weather_location).convert("RGB")
                        )
                        prevTime = currentTime
                    print(e)
                    time.sleep(1)
            else:
                matrix.clear()
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()
