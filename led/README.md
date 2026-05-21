# LED

A minimal embedded-lab example showing how to control an LED via GPIO on a Linux SBC. Includes a Python script plus `pinctrl` commands to turn the LED on/off, read pin state, and reset the pin.

## Prerequisites

```bash
sudo apt update
sudo apt install -y python3-gpiozero python3-lgpio
```

## Tips

- Use `pinout` command to check the schema of the GPIO pins.

## Wiring

GPIO17 (11) -> Breadboard (+) -> Resistor (220 Ω) -> LED long leg (+, anode)
GND (6) -> Breadboard (-) -> LED short leg (-, cathode)

## How to?

Manually, turn on the LED:
```bash
pinctrl set 17 op dh
```

and to turn off:
```bash
pinctrl set 17 op dl
```

To get the state of the GPIO pin, run:
```bash
pinctrl get 17
```

To reset the GPIO pin state, run:
```bash
pinctrl set 17 no
```

Run `led.py` like to play with the LED:
```bash
python led.py
```
