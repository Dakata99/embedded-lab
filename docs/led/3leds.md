# LED

A traffic light simulation via 3 LEDs - red, yellow and green.

## Wiring

```
GPIO18 (12) -> Breadboard (+) -> Resistor (220 Ω) -> Red LED long leg (+, anode)
GPIO24 (18) -> Breadboard (+) -> Resistor (220 Ω) -> Yellow LED long leg (+, anode)
GPIO25 (22) -> Breadboard (+) -> Resistor (220 Ω) -> Green LED long leg (+, anode)
GND    (14) -> Breadboard (-) -> LED short leg (-, cathode)
```

## How to run?

Firstly, go to the folder:
```bash
cd led
```

Then run `3led.py`:
```bash
python 3led.py
```
