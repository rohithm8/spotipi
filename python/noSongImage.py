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
        thumbFilename = os.path.join(dir, f'../images/{str(currentWeather.kind)} Night.png') # if it's night time, use the night icon
    draw.text((64, 0), tempText, fill=ImageColor.getrgb("white"), font=font, anchor="ra")
    weatherIcon = Image.open(thumbFilename).convert("RGBA")
    image.alpha_composite(weatherIcon, (64-20, 8))
    calendarInfo = getCalendarInfo()
    lineQuota = 7 # 7 lines of text can be displayed
    if calendarInfo is None:
        # None means there was an error, so display caution image
        image.alpha_composite(Image.open((os.path.join(dir, '../images/NoCal.png'))).convert("RGBA"), (0, 32))
        return image
    elif calendarInfo:
        for event in calendarInfo:
            calendarSummary = fill(event[2], width=16)
            start, end = [datetime.fromisoformat(event[i].replace('Z', '+00:00')).replace(tzinfo=None) for i in range(2)]
            calendarTime = "Now" if start < datetime.now() < end else start.strftime("%H:%M") # if the event is happening now, display "Now" instead of the start time
            calendarItem = "\n".join((calendarTime, calendarSummary))
            if lineQuota > calendarItem.count("\n"):
                draw.multiline_text((1, 23 + (7-lineQuota)*6), calendarItem.upper(), fill=ImageColor.getrgb(event[3]+"b3"), font=smallfont, spacing=1)
                lineQuota -= calendarItem.count("\n") + 1
            else:
                return image
    return image

if __name__ == '__main__':
    noSongImage((64,64), "London").convert("RGB").save("noSongImage.png") # for testing
