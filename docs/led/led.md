# LED

A minimal embedded-lab example showing how to control an LED via GPIO on a Linux SBC.

## Wiring

```
GPIO17 (11) -> Breadboard (+) -> Resistor (220 Ω) -> LED long leg (+, anode)
GND    (6)  -> Breadboard (-) -> LED short leg (-, cathode)
```

## How to run?

Firstly, go to the folder:
```bash
cd led
```

Then run `led.py` to play with the LED:
```bash
python led.py
```
