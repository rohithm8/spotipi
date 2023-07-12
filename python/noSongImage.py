from PIL import Image, ImageDraw, ImageFont, ImageColor
import time, sys, os


def noSongImage():
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)
    dir = os.path.dirname(__file__)
    font = ImageFont.truetype(os.path.join(dir, '../fonts/5x7.ttf'), 8)
    timetext = time.strftime("%H:%M:%S")
    draw.text((0, 0), timetext, fill=ImageColor.getrgb("white"), font=font)
    return image

# noSongImage().save("noSongImage.png")