# app.py

# also importing the request module
import sys, os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from flask import Flask, render_template, request, redirect, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import configparser

import dbus

app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"

dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "config")
)
filename = os.path.join(dir, "rgb_options.ini")

# Configuration for the matrix
config = configparser.ConfigParser()
config.read(filename)

sysbus = dbus.SystemBus()
systemd1 = sysbus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
manager = dbus.Interface(systemd1, "org.freedesktop.systemd1.Manager")

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


# home route
@app.route("/")
def saved_config():
    # Brightness from config file
    brightness = int(config["DEFAULT"]["brightness"])
    width = int(config["DEFAULT"]["rows"])
    height = int(config["DEFAULT"]["columns"])
    power = config["DEFAULT"]["power"]
    refresh_rate = config["DEFAULT"]["refresh_rate"]
    weather_location = config["DEFAULT"]["weather_location"]
    schedule_start = config["DEFAULT"]["schedule_start"]
    schedule_end = config["DEFAULT"]["schedule_end"]
    return render_template(
        "index.html",
        brightness=brightness,
        width=width,
        height=height,
        power=power,
        refresh_rate=refresh_rate,
        weather_location=weather_location,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
    )


# handling power status
@app.route("/power", methods=["GET", "POST"])
def handle_power():
    power = request.form["power"]
    brightness = int(config["DEFAULT"]["brightness"])
    width = int(config["DEFAULT"]["rows"])
    height = int(config["DEFAULT"]["columns"])
    weather_location = config["DEFAULT"]["weather_location"]
    schedule_start = config["DEFAULT"]["schedule_start"]
    schedule_end = config["DEFAULT"]["schedule_end"]
    config.set("DEFAULT", "power", request.form["power"])
    if power == "on":
        job = manager.StartUnit("spotipi.service", "replace")
    else:
        job = manager.StopUnit("spotipi.service", "replace")
    return render_template(
        "index.html",
        brightness=brightness,
        width=width,
        height=height,
        weather_location=weather_location,
        power=power,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
    )


# handling form data
@app.route("/brightness", methods=["POST"])
def handle_brightness():
    config.set("DEFAULT", "brightness", request.form["brightness"])
    width = int(config["DEFAULT"]["rows"])
    height = int(config["DEFAULT"]["columns"])
    power = config["DEFAULT"]["power"]
    weather_location = config["DEFAULT"]["weather_location"]
    schedule_start = config["DEFAULT"]["schedule_start"]
    schedule_end = config["DEFAULT"]["schedule_end"]
    with open(filename, "w") as configfile:
        config.write(configfile)
    job = manager.RestartUnit("spotipi.service", "fail")
    return render_template(
        "index.html",
        brightness=request.form["brightness"],
        width=width,
        height=height,
        weather_location=weather_location,
        power=power,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
    )


# handling form data
@app.route("/size", methods=["POST"])
def handle_size():
    config.set("DEFAULT", "rows", request.form["width"])
    config.set("DEFAULT", "columns", request.form["height"])
    brightness = int(config["DEFAULT"]["brightness"])
    power = config["DEFAULT"]["power"]
    weather_location = config["DEFAULT"]["weather_location"]
    schedule_start = config["DEFAULT"]["schedule_start"]
    schedule_end = config["DEFAULT"]["schedule_end"]
    with open(filename, "w") as configfile:
        config.write(configfile)
    job = manager.RestartUnit("spotipi.service", "fail")
    return render_template(
        "index.html",
        brightness=brightness,
        width=int(request.form["width"]),
        height=int(request.form["height"]),
        weather_location=weather_location,
        power=power,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
    )


# handling form data
@app.route("/refresh-rate", methods=["POST"])
def handle_refresh_rate():
    config.set("DEFAULT", "refresh_rate", request.form["refresh_rate"])
    brightness = int(config["DEFAULT"]["brightness"])
    power = config["DEFAULT"]["power"]
    width = int(config["DEFAULT"]["rows"])
    height = int(config["DEFAULT"]["columns"])
    weather_location = config["DEFAULT"]["weather_location"]
    schedule_start = config["DEFAULT"]["schedule_start"]
    schedule_end = config["DEFAULT"]["schedule_end"]
    with open(filename, "w") as configfile:
        config.write(configfile)
    job = manager.RestartUnit("spotipi.service", "fail")
    return render_template(
        "index.html",
        brightness=brightness,
        width=width,
        height=height,
        refresh_rate=int(request.form["refresh_rate"]),
        weather_location=weather_location,
        power=power,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
    )


# handling form data
@app.route("/location", methods=["POST"])
def handle_location():
    config.set(
        "DEFAULT",
        "weather_location",
        request.form["weather_location"].replace(" ", "+"),
    )
    brightness = int(config["DEFAULT"]["brightness"])
    width = int(config["DEFAULT"]["rows"])
    height = int(config["DEFAULT"]["columns"])
    power = config["DEFAULT"]["power"]
    refresh_rate = config["DEFAULT"]["refresh_rate"]
    schedule_start = config["DEFAULT"]["schedule_start"]
    schedule_end = config["DEFAULT"]["schedule_end"]
    with open(filename, "w") as configfile:
        config.write(configfile)
    job = manager.RestartUnit("spotipi.service", "fail")
    return render_template(
        "index.html",
        brightness=brightness,
        width=width,
        height=height,
        refresh_rate=refresh_rate,
        weather_location=request.form["weather_location"],
        power=power,
        schedule_start=schedule_start,
        schedule_end=schedule_end,
    )


@app.route("/schedule", methods=["POST"])
def handle_schedule():
    config.set("DEFAULT", "schedule_start", request.form["schedule_start"])
    config.set("DEFAULT", "schedule_end", request.form["schedule_end"])
    brightness = int(config["DEFAULT"]["brightness"])
    width = int(config["DEFAULT"]["rows"])
    height = int(config["DEFAULT"]["columns"])
    power = config["DEFAULT"]["power"]
    refresh_rate = config["DEFAULT"]["refresh_rate"]
    weather_location = config["DEFAULT"]["weather_location"]
    with open(filename, "w") as configfile:
        config.write(configfile)
    job = manager.RestartUnit("spotipi.service", "fail")
    return render_template(
        "index.html",
        brightness=brightness,
        width=width,
        height=height,
        refresh_rate=refresh_rate,
        weather_location=weather_location,
        power=power,
        schedule_start=request.form["schedule_start"],
        schedule_end=request.form["schedule_end"],
    )


@app.route("/login")
def login():
    flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(dir, "credentials.json"),
        SCOPES,
    )
    flow.redirect_uri = url_for("callback", _external=True)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow = InstalledAppFlow.from_client_secrets_file(
        os.path.join(dir, "credentials.json"),
        SCOPES,
    )
    flow.redirect_uri = url_for("callback", _external=True)

    https_authorization_url = request.url_root.replace("http://", "https://")
    print(request.url, request.url_root, request.host_url, request.base_url)
    flow.fetch_token(authorization_response=https_authorization_url)
    creds = flow.credentials
    with open(os.path.join(dir, "token.json"), "w") as token:
        token.write(creds.to_json())
    return redirect(url_for("saved_config"))


app.run(host="http://0.0.0.0", port=80)
