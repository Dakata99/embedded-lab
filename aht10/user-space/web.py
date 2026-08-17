from flask import Flask, render_template, jsonify
import board
import adafruit_ahtx0
import time
import threading
from loguru import logger

MEASUREMENTS: dict[str, float | int] = {"temperature": None, "humidity": None}

AHT10 = adafruit_ahtx0.AHTx0(board.I2C())

TEMPERATURE_MAPPING: dict = {
    "Cold": lambda temp: temp < 16,
    "Comfortable": lambda temp: temp >= 16 and temp < 20,
    "Hot": lambda temp: temp >= 20,
}

HUMIDITY_MAPPING: dict = {
    "Dry": lambda humidity: humidity < 30,
    "Normal": lambda humidity: humidity >= 30 and humidity < 60,
    "Humid": lambda humidity: humidity > 60,
}


def poll(sensor):
    logger.debug("Polling temperature and humidity values...")
    while True:
        MEASUREMENTS["temperature"] = sensor.temperature
        MEASUREMENTS["humidity"] = sensor.relative_humidity
        time.sleep(1)


def get_status(value: float, mapping: dict) -> str:
    for status, expression in mapping.items():
        if expression(value):
            return status
    return "Unknown"


web = Flask(__name__)


@web.route("/")
def index():
    return render_template(
        "index.html",
        temperature=MEASUREMENTS["temperature"],
        humidity=MEASUREMENTS["humidity"],
        temperature_status=get_status(MEASUREMENTS["temperature"], TEMPERATURE_MAPPING),
        humidity_status=get_status(MEASUREMENTS["humidity"], HUMIDITY_MAPPING),
    )


@web.get("/api/env")
def env():
    return jsonify({
        'temperature': MEASUREMENTS["temperature"],
        'humidity': MEASUREMENTS["humidity"],
        'temperature-status': get_status(MEASUREMENTS["temperature"], TEMPERATURE_MAPPING),
        'humidity-status': get_status(MEASUREMENTS["humidity"], HUMIDITY_MAPPING),
    })


threading.Thread(target=poll, args=(AHT10,), daemon=True).start()
