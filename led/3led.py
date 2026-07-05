import threading
from time import sleep

from gpiozero import PWMLED

# BCM numbering means the code uses the GPIO number, not the physical pin number.
# So LED(18) means GPIO18, which is located on physical pin 12.
RED_LED_PIN = 18
red = PWMLED(RED_LED_PIN)

YELLOW_LED_PIN = 24
yellow = PWMLED(YELLOW_LED_PIN)

GREEN_LED_PIN = 25
green = PWMLED(GREEN_LED_PIN)

print("Raspberry Pi 3 LED control")

stop_event = threading.Event()


def input_thread() -> None:
    input("Enter 'q' to stop...\n")
    stop_event.set()


def worker_thread() -> None:
    try:
        while not stop_event.is_set():
            red.on()
            sleep(1)
            red.off()
            yellow.on()
            sleep(1)
            yellow.off()
            green.on()
            sleep(1)
            green.off()
    finally:
        red.off()
        yellow.off()
        green.off()
        red.close()
        yellow.close()
        green.close()


threading.Thread(target=input_thread, daemon=True).start()
worker_thread()

print("Goodbye.")
