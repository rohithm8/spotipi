from PIL import Image, ImageDraw, ImageFont, ImageColor
from textwrap import fill
import python_weather
import os.path
from datetime import date, datetime
import time
import asyncio
from getCalendarInfo import getCalendarInfo

async def getWeather(weather_location="London"):
    client = python_weather.Client()
    weather = await client.get(weather_location)
    await client.close()
    return weather

def noSongImage(size=(64, 64), weather_location="London"):
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    dir = os.path.dirname(__file__)
    font = ImageFont.truetype(os.path.join(dir, '../fonts/5x7.ttf'), 8)
    smallfont = ImageFont.truetype(os.path.join(dir, '../fonts/3x5.ttf'), 8)
    timetext = time.strftime("%H:%M", time.localtime())
    datetext = date.today().strftime("%b %d")
    draw.text((1, 0), timetext, fill=ImageColor.getrgb("white"), font=font)
    draw.text((1, 8), datetext, fill=ImageColor.getrgb("white"), font=font)
    weather = asyncio.run(getWeather(weather_location))
    currentWeather, forecastWeather = weather.current, weather.forecasts
    tempText = str(currentWeather.temperature) + "C"
    sunSet = next(forecastWeather).astronomy.sun_set
    sunRise = next(forecastWeather).astronomy.sun_rise
    if sunRise < datetime.now().time() < sunSet:
        thumbFilename = os.path.join(dir, f'../images/{str(currentWeather.kind)}.png')
    else:
        thumbFilename = os.path.join(dir, f'../images/{str(currentWeather.kind)} Night.png')
    draw.text((64, 0), tempText, fill=ImageColor.getrgb("white"), font=font, anchor="ra")
    weatherIcon = Image.open(thumbFilename).convert("RGBA")
    image.alpha_composite(weatherIcon, (64-20, 8))
    calendarInfo = getCalendarInfo()
    if calendarInfo is not None:
        calendarSummary = fill(calendarInfo[1], width=16)
        calendarTime = calendarInfo[0][11:16]
        draw.text((1, 21), calendarTime, fill=ImageColor.getrgb("gray"), font=smallfont)
        draw.multiline_text((1, 29), calendarSummary, fill=ImageColor.getrgb("gray"), font=smallfont)
    return image

# noSongImage((64,64), "London").convert("RGB").save("noSongImage.png") # for testing
