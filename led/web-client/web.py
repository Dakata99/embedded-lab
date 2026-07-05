from flask import Flask, render_template, request, jsonify
import atexit
from pathlib import Path
import json
from loguru import logger
from ledmanager import LedManager

app = Flask(__name__)

led_manager = LedManager()

@app.route("/")
def index():
    configfile = Path(__file__).parent / 'config.json'

    with open(configfile) as fd:
        metadata = json.load(fd)

    leds = metadata['leds']
    if not led_manager.configured():
        for led in leds:
            led_manager.register(led['id'], led['gpio'])

    return render_template("index.html", leds=leds)

@app.post("/api/leds/action")
def led_action():
    data = request.get_json(silent=True) or {}

    scope = data.get("scope")
    command = data.get("command")

    logger.debug(f"Full posted JSON: {data}")

    if scope == "led":
        led_id = data.get("led_id")
        gpio_pin = data.get("gpio_pin")
        enabled = data.get("enabled")

        logger.debug(f"Selected LED: {led_id}")
        logger.debug(f"GPIO pin: {gpio_pin}")
        logger.debug(f"Command: {command}")
        logger.debug(f"Enabled: {enabled}")

        payload = {"led_id": led_id}
        if enabled is not None:
            payload["enable"] = enabled

        led_manager.handle_action(scope, command, **payload)

        return jsonify({"status": "ok"})
    elif scope == "all":
        logger.debug(f"Global command: {command}")
        led_manager.handle_action(scope, command)

        return jsonify({"status": "ok"})

    return jsonify({
        "status": "error",
        "message": "Invalid payload",
        "received": data
    }), 400


atexit.register(led_manager.cleanup)
