#!/usr/bin/python

from gpiozero import PWMLED

# BCM numbering means the code uses the GPIO number, not the physical pin number.
# So LED(17) means GPIO17, which is located on physical pin 11.
LED_PIN = 17
led = PWMLED(LED_PIN)

commands = ["on", "off", "blink", "pulse", "quit"]
print("Raspberry Pi LED control")
print(f"Commands: {', '.join(commands)}")

try:
    while True:
        command = input("> ").strip().lower()
        if command == "on":
            led.on()
            print("LED is ON")
        elif command == "off":
            led.off()
            print("LED is OFF")
        elif command == "blink":
            led.blink(on_time=0.5, off_time=0.5)
            print("LED is blinking")
        elif command == "pulse":
            led.pulse()
            print("LED is pulsing")
        elif command in {"quit", "exit", "q"}:
            led.off()
            print("Goodbye.")
            break
        else:
            print(f"Unknown command. Use: {', '.join(commands)}")
finally:
    led.off()
    led.close()
