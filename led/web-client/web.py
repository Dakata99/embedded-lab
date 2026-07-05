from flask import Flask, render_template, request, jsonify
import atexit
from pathlib import Path
import json
from loguru import logger
from ledmanager import LedManager
import os

HOSTIP: str = os.environ.get("HOSTIP", "0.0.0.0").strip()
PORT: int = int(os.environ.get("PORT", 5000))
LED_CONFIG: Path = Path(os.environ.get("LED_CONFIG", Path(__file__).parent / "config.json"))

app = Flask(__name__)

led_manager = LedManager()

@app.route("/")
def index():
    with open(LED_CONFIG) as fd:
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


if __name__ == "__main__":
    app.run(
        host=HOSTIP,
        port=PORT,
        debug=False,
        use_reloader=False,
    )
    atexit.register(led_manager.cleanup)
else:
    atexit.register(led_manager.cleanup)
