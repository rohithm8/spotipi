from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
from textwrap import fill
import aiohttp
import os.path
from datetime import date, datetime
import time
from getCalendarInfo import getCalendarInfo

dir = os.path.dirname(__file__)
font = ImageFont.truetype(os.path.join(dir, '../fonts/5x7.ttf'), 8)
smallfont = ImageFont.truetype(os.path.join(dir, '../fonts/3x5.ttf'), 8)
WEATHER_CODE_MAPPING = {
	113: "Sunny",
	116: "Partly Cloudy",
	119: "Cloudy",
	122: "Very Cloudy",
	143: "Fog",
	176: "Light Showers",
	179: "Light Sleet Showers",
	182: "Light Sleet",
	185: "Light Sleet",
	200: "Thundery Showers",
	227: "Light Snow",
	230: "Heavy Snow",
	248: "Fog",
	260: "Fog",
	263: "Light Showers",
	266: "Light Rain",
	281: "Light Sleet",
	284: "Light Sleet",
	293: "Light Rain",
	296: "Light Rain",
	299: "Heavy Showers",
	302: "Heavy Rain",
	305: "Heavy Showers",
	308: "Heavy Rain",
	311: "Light Sleet",
	314: "Light Sleet",
	317: "Light Sleet",
	320: "Light Snow",
	323: "Light Snow Showers",
	326: "Light Snow Showers",
	329: "Heavy Snow",
	332: "Heavy Snow",
	335: "Heavy Snow Showers",
	338: "Heavy Snow",
	350: "Light Sleet",
	353: "Light Showers",
	356: "Heavy Showers",
	359: "Heavy Rain",
	362: "Light Sleet Showers",
	365: "Light Sleet Showers",
	368: "Light Snow Showers",
	371: "Heavy Snow Showers",
	374: "Light Sleet Showers",
	377: "Light Sleet",
	386: "Thundery Showers",
	389: "Thundery Heavy Rain",
	392: "Thundery Snow Showers",
	395: "Heavy Snow Showers",
}




@dataclass
class Weather:
    temperature: float
    weather_code: int
    sunrise: datetime.time
    sunset: datetime.time

    @property
    def thumbnail_path(self):
        weather_kind = WEATHER_CODE_MAPPING[self.weather_code]
        if self.sunrise < datetime.now().time() < self.sunset:
            return os.path.join(dir, f'../images/{weather_kind}.png')
        else:
            return os.path.join(dir, f'../images/{weather_kind} Night.png')



async def get_weather(weather_location="London"):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://wttr.is/{weather_location}?format=j2") as response:
            return await response.json()



def noSongImage(size=(64, 64), weather_location="London"):
    image = Image.new("RGBA", size)
    draw = ImageDraw.Draw(image)
    timetext = time.strftime("%H:%M", time.localtime())
    datetext = date.today().strftime("%b %d")
    draw.text((1, 0), timetext, fill=ImageColor.getrgb("white"), font=font)
    draw.text((1, 8), datetext, fill=ImageColor.getrgb("white"), font=font)
    # weather_json = asyncio.run(get_weather(weather_location))
    weather_json = requests.get(f"https://wttr.in/{weather_location}?format=j2").json()
    weather = Weather(
        temperature=weather_json["current_condition"][0]["temp_C"],
        weather_code=int(weather_json["current_condition"][0]["weatherCode"]),
        sunrise=datetime.strptime(weather_json["weather"][0]["astronomy"][0]["sunrise"], "%I:%M %p").time(),
        sunset=datetime.strptime(weather_json["weather"][0]["astronomy"][0]["sunset"], "%I:%M %p").time()
    )
    tempText = str(weather.temperature) + "C"
    draw.text((64, 0), tempText, fill=ImageColor.getrgb("white"), font=font, anchor="ra")
    weatherIcon = Image.open(weather.thumbnail_path).convert("RGBA")
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
