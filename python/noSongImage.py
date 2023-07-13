from PIL import Image, ImageDraw, ImageFont, ImageColor
import python_weather
import os
from datetime import date, datetime
import time
import asyncio

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
    timetext = time.strftime("%H:%M", time.localtime())
    datetext = date.today().strftime("%b %d")
    draw.text((1, 0), timetext, fill=ImageColor.getrgb("white"), font=font)
    draw.text((1, 8), datetext, fill=ImageColor.getrgb("white"), font=font)
    weather = asyncio.run(getWeather(weather_location))
    currentWeather, forecastWeather = weather.current, weather.forecasts
    tempText = str(currentWeather.temperature) + "C"
    sunSet = next(forecastWeather).astronomy.sun_set
    sunRise = next(forecastWeather).astronomy.sun_rise
    if sunSet < datetime.now().time() < sunRise:
        thumbFilename = os.path.join(dir, f'../images/{str(currentWeather.kind)}.png')
    else:
        thumbFilename = os.path.join(dir, f'../images/{str(currentWeather.kind)} Night.png')
    draw.text((64, 0), tempText, fill=ImageColor.getrgb("white"), font=font, anchor="ra")
    weatherIcon = Image.open(thumbFilename).convert("RGBA")
    image.alpha_composite(weatherIcon, (64-20, 8))
    return image

# noSongImage().convert("RGB").save("noSongImage.png") # for testing
