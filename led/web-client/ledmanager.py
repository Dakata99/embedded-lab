from loguru import logger
from gpiozero import PWMLED

class Led:
    def __init__(self, led_label , gpio, supports):
        self._led_label = led_label
        self._gpio = gpio
        self._supports = supports
        self._pwm_led = PWMLED(gpio)
        self._enabled = True

    def __init__(self, metadata: dict):
        self._led_label = metadata.get("label")
        self._gpio = metadata.get("gpio")
        self._supports = metadata.get("supports", [])
        self._pwm_led = PWMLED(self._gpio) if self._gpio is not None else None
        self._enabled = True if self._pwm_led is not None else False

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    def on(self):
        if self._enabled and 'on' in self._supports:
            logger.debug(f"Turning ON LED {self._led_label} (GPIO: {self._gpio})")
            self._pwm_led.on()
        else:
            logger.warning(f"LED {self._led_label} (GPIO: {self._gpio}) is disabled or does not support 'on' command.")

    def off(self):
        if self._enabled and 'off' in self._supports:
            logger.debug(f"Turning OFF LED {self._led_label} (GPIO: {self._gpio})")
            self._pwm_led.off()
        else:
            logger.warning(f"LED {self._led_label} (GPIO: {self._gpio}) is disabled or does not support 'off' command.")

    def blink(self, on_time=0.5, off_time=0.5):
        if self._enabled and 'blink' in self._supports:
            logger.debug(f"Blinking LED {self._led_label} (GPIO: {self._gpio})")
            self._pwm_led.blink(on_time=on_time, off_time=off_time)
        else:
            logger.warning(f"LED {self._led_label} (GPIO: {self._gpio}) is disabled or does not support 'blink' command.")

    def pulse(self):
        if self._enabled and 'pulse' in self._supports:
            logger.debug(f"Pulsing LED {self._led_label} (GPIO: {self._gpio})")
            self._pwm_led.pulse()
        else:
            logger.warning(f"LED {self._led_label} (GPIO: {self._gpio}) is disabled or does not support 'pulse' command.")

    def close(self):
        logger.debug(f"Cleaning up LED {self._led_label} (GPIO: {self._gpio})")
        self._pwm_led.off()
        self._pwm_led.close()

class LedManager:
    def __init__(self):
        self._leds: dict[str, Led] = {}
        self._actions: dict = {
            'on': self._on,
            'off': self._off,
            'blink': self._blink,
            'pulse': self._pulse,
            'enable': self._enable,
            'all-on': self._all_on,
            'all-off': self._all_off,
            'all-blink': self._all_blink,
            'all-pulse': self._all_pulse
        }

    def register(self, led_id, gpio, supports):
        logger.debug(f"Registering LED (ID: {led_id}, GPIO: {gpio})...")
        self._leds[led_id] = Led(led_id, gpio, supports)

    def register(self, led_id, led: Led):
        logger.debug(f"Registering LED (Label: {led._led_label}, GPIO: {led._gpio})...")
        self._leds[led_id] = led

    def _on(self, **kwargs):
        led_id = kwargs.get('led_id')
        logger.debug(f"Turning on LED {led_id}...")
        self._leds[led_id].on()

    def _off(self, **kwargs):
        led_id = kwargs.get('led_id')
        logger.debug(f"Turning off LED {led_id}...")
        self._leds[led_id].off()

    def _blink(self, **kwargs):
        led_id = kwargs.get('led_id')
        logger.debug(f"Blinking LED {led_id}...")
        self._leds[led_id].blink(on_time=0.2, off_time=0.2)

    def _pulse(self, **kwargs):
        led_id = kwargs.get('led_id')
        logger.debug(f"Pulsing LED {led_id}...")
        self._leds[led_id].pulse()

    def _enable(self, **kwargs):
        led_id = kwargs.get('led_id')
        enable = kwargs.get('enable')
        logger.debug(f"LED {led_id} enabled: {enable}")
        self._leds[led_id].enabled = enable

    def _all_on(self):
        logger.debug('Turning ON all LEDs...')
        for led in self._leds.values():
            led.on()

    def _all_off(self):
        logger.debug('Turning OFF all LEDs...')
        for led in self._leds.values():
            led.off()

    def _all_blink(self):
        logger.debug('Blink all LEDs...')
        for led in self._leds.values():
            led.blink(on_time=0.2, off_time=0.2)

    def _all_pulse(self):
        logger.debug('Pulse all LEDs...')
        for led in self._leds.values():
            led.pulse()

    def handle_action(self, scope, action, **kwargs):
        if scope == 'all':
            self._actions[action]()
        else:
            self._actions[action](**kwargs)

    def cleanup(self):
        logger.debug("Cleaning up...")
        for led in self._leds.values():
            led.close()

    def configured(self):
        return self._leds

