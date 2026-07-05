from flask import Flask, render_template, request, jsonify
import board
import adafruit_ahtx0
import time
import threading
from loguru import logger

MEASUREMENTS: dict[str, float|int] = {
    'temperature': None,
    'humidity': None
}

AHT10 = adafruit_ahtx0.AHTx0(board.I2C())

TEMP_MAPPING: dict = {
    'cold': lambda temp: temp < 16,
    'comfortable': lambda temp: temp >= 16 and temp < 20,
    'hot': lambda temp: temp >= 20,
}

HUM_MAPPING: dict = {
    'dry': lambda humidity: humidity < 30,
    'normal': lambda humidity: humidity >= 30 and humidity < 60,
    'humid': lambda humidity: humidity > 60,
}

def poll(sensor):
    while True:
        MEASUREMENTS['temperature'] = sensor.temperature
        MEASUREMENTS['humidity'] = sensor.relative_humidity
        time.sleep(1)

def get_status(value: float, mapping: dict) -> str:
    for status, expression in mapping.items():
        if expression(value):
            return status


web = Flask(__name__)

@web.route("/")
def index():
    return render_template(
        "index.html",
        temperature=MEASUREMENTS['temperature'],
        humidity=MEASUREMENTS['humidity'],
        temp_status=get_status(MEASUREMENTS['temperature'], TEMP_MAPPING).capitalize(),
        humid_status=get_status(MEASUREMENTS['humidity'], HUM_MAPPING).capitalize()
    )

@web.get("/api/env")
def env():
    return MEASUREMENTS

threading.Thread(target=poll, args=(AHT10,), daemon=True).start()
