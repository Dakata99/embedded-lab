from loguru import logger
from gpiozero import PWMLED


class LedManager:
    def __init__(self):
        self._leds: dict[str, (PWMLED, bool)] = {}
        self._actions: dict = {
            "on": self._on,
            "off": self._off,
            "blink": self._blink,
            "pulse": self._pulse,
            "enable": self._enable,
            "all-on": self._all_on,
            "all-off": self._all_off,
            "all-blink": self._all_blink,
            "all-pulse": self._all_pulse,
        }

    def register(self, led_id, gpio):
        logger.debug(f"Registering LED (ID: {led_id}, GPIO: {gpio})...")
        self._leds[led_id] = (PWMLED(gpio), True)

    def _on(self, **kwargs):
        led_id = kwargs.get("led_id")
        logger.debug(f"Turning on LED {led_id}...")
        self._leds[led_id][0].on()

    def _off(self, **kwargs):
        led_id = kwargs.get("led_id")
        logger.debug(f"Turning off LED {led_id}...")
        self._leds[led_id][0].off()

    def _blink(self, **kwargs):
        led_id = kwargs.get("led_id")
        logger.debug(f"Blinking LED {led_id}...")
        self._leds[led_id][0].blink(on_time=0.2, off_time=0.2)

    def _pulse(self, **kwargs):
        led_id = kwargs.get("led_id")
        logger.debug(f"Pulsing LED {led_id}...")
        self._leds[led_id][0].pulse()

    def _enable(self, **kwargs):
        led_id = kwargs.get("led_id")
        enable = kwargs.get("enable")
        logger.debug(f"LED {led_id} enabled: {enable}")
        self._leds[led_id] = (self._leds[led_id][0], enable)

    def _all_on(self):
        logger.debug("Turning ON all LEDs...")
        for led in self._leds.values():
            if led[1]:  # Check if LED is enabled
                led[0].on()

    def _all_off(self):
        logger.debug("Turning OFF all LEDs...")
        for led in self._leds.values():
            if led[1]:  # Check if LED is enabled
                led[0].off()

    def _all_blink(self):
        logger.debug("Blink all LEDs...")
        for led in self._leds.values():
            if led[1]:  # Check if LED is enabled
                led[0].blink(on_time=0.2, off_time=0.2)

    def _all_pulse(self):
        logger.debug("Pulse all LEDs...")
        for led in self._leds.values():
            if led[1]:  # Check if LED is enabled
                led[0].pulse()

    def handle_action(self, scope, action, **kwargs):
        if scope == "all":
            self._actions[action]()
        else:
            self._actions[action](**kwargs)

    def cleanup(self):
        logger.debug("Cleaning up...")
        for led in self._leds.values():
            led[0].off()
            led[0].close()

    def configured(self):
        return self._leds
