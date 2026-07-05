# Web client for LED control

A learning-oriented project guide for controlling three physical LEDs from a browser-based GUI on your PC.

## Overview

Run a small service on the Raspberry Pi. Your PC browser opens a web page served by that service.
The page asks the Pi which LEDs exist, renders one control card per LED, and sends commands such as
on, off, blink or pulse back to the Pi.

## Wiring

```
GPIO18 (12) -> Breadboard (+) -> Resistor (220 Ω) -> Red LED long leg (+, anode)
GPIO24 (18) -> Breadboard (+) -> Resistor (220 Ω) -> Yellow LED long leg (+, anode)
GPIO25 (22) -> Breadboard (+) -> Resistor (220 Ω) -> Green LED long leg (+, anode)
GND    (14) -> Breadboard (-) -> LED short leg (-, cathode)
```

## How to run?

Firstly, setup the environment:
```bash
. setupenv
```

then run:
```bash
flask --app led/web-client/web.py run --host $(hostname -I)
```

Use `--debug` option to enable reloading (while developing).

## LED registry

A simple LED connected to a GPIO pin has no identity, no address, and no way to announce *"I exist"*.
The Pi cannot magically know that a wire and LED are attached to GPIO17 unless you design a detection circuit.

Instead, an LED registry is used on the Raspberry Pi. That registry is the source of truth.
The client asks the Pi for that registry when the page loads.

The LED registry is represented by a small configuration JSON file.
The backend exposes the LEDS through an endpoint such as `GET /api/leds`.
```json
{
    "leds": [
        {
            "id": "led-1",
            "label": "Red LED",
            "gpio": 18
        },
        {
            "id": "led-2",
            "label": "Yellow LED",
            "gpio": 24
        },
        {
            "id": "led-3",
            "label": "Green LED",
            "gpio": 25
        }
    ]
}
```

> File: `led/web-client/config.json`.

## TODOs

- Add effects - treat blink and pulse as commands with parameters (add to GUI).
- Add `supports` field for supported commands in the JSON file (and GUI).
- Add service to systemd.
