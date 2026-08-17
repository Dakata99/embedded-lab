from flask import Flask, render_template, jsonify
from loguru import logger
from pathlib import Path
from typing import Optional
import os

HOSTIP: str = os.environ.get("HOSTIP", "0.0.0.0").strip()
PORT: int = int(os.environ.get("PORT", 5000))

# --- hwmon --
class Hwmon():
    I2C_DEVICE: Path = Path('/sys/bus/i2c/devices/1-0038')

    def __init__(self):
        self._hwmon_root: Path = self.I2C_DEVICE / 'hwmon'

        if not self._hwmon_root.exists():
            raise RuntimeError(f"hwmon directory not found: {self._hwmon_root}")

        hwmon_dirs = list(self._hwmon_root.glob('hwmon*'))

        if not hwmon_dirs:
            raise RuntimeError(f"no hwmon dirs found under: {self._hwmon_root}")
    
        hwmon_dir = hwmon_dirs[0]
        self._temperature: Path = hwmon_dir / 'temp1_input'
        self._humidity: Path = hwmon_dir / 'humidity1_input'

        if not self._temperature.exists():
            raise RuntimeError(f'missing temperature file: {self._temperature}')

        if not self._humidity.exists():
            raise RuntimeError(f'missing humidity file: {self._humidity}')

    def read_temperature(self):
        return int(self._temperature.read_text().strip()) / 1000

    def read_humidity(self):
        return int(self._humidity.read_text().strip()) / 1000

    def read(self):
        temperature: int = self.read_temperature()
        humidity: int = self.read_humidity()
    
        return {
            "temperature": temperature,
            "humidity": humidity,
            "temperature-status": get_status(temperature, TEMP_MAPPING),
            "humidity-status": get_status(humidity, HUM_MAPPING)
        }

HWMON: Optional[Hwmon] = None

def get_hwmon() -> Hwmon:
    global HWMON

    if HWMON is None:
        return Hwmon()

    return HWMON

# --- helpers ---

TEMP_MAPPING: dict = {
    "Cold": lambda temp: temp < 16,
    "Comfortable": lambda temp: temp >= 16 and temp < 20,
    "Hot": lambda temp: temp >= 20,
}

HUM_MAPPING: dict = {
    "Dry": lambda humidity: humidity < 30,
    "Normal": lambda humidity: humidity >= 30 and humidity < 60,
    "Humid": lambda humidity: humidity > 60,
}

def get_status(value: float, mapping: dict) -> str:
    for status, expression in mapping.items():
        if expression(value):
            return status
    return "Unknown"

# --- web client ---
web = Flask(__name__)

@web.route("/")
def index():
    try:
        data: dict[str, int | str] = get_hwmon().read()
        
        return render_template(
            "index.html",
            sensor_ok=True,
            temperature=data['temperature'],
            humidity=data['humidity'],
            temp_status=data['temperature-status'],
            humid_status=data['humidity-status'],
            error=None
        )
    except Exception as e:
        logger.error(f"Sensor unavailable: {e}")

        return render_template(
            "index.html",
            sensor_ok=False,
            temperature=None,
            humidity=None,
            temp_status="Unknown",
            humid_status="Unknown",
            error=str(e)
        )

@web.get("/sensor-data")
def env():
    try:
        data: dict[str, int | str] = get_hwmon().read()

        return jsonify({
            "ok": True,
            **data
        })
    except Exception as e:
        logger.error(f"Sensor unavailable: {e}")
        
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 503

if __name__ == "__main__":
    web.run(
        host=HOSTIP,
        port=PORT,
        debug=False,
        use_reloader=False,
    )
