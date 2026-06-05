#!/usr/bin/python

import threading
from time import sleep

from gpiozero import PWMLED

# BCM numbering means the code uses the GPIO number, not the physical pin number.
# So LED(17) means GPIO17, which is located on physical pin 11.
RED_LED_PIN = 17
red = PWMLED(RED_LED_PIN)

YELLOW_LED_PIN = 10
yellow = PWMLED(YELLOW_LED_PIN)

GREEN_LED_PIN = 7
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
