# LED

A traffic light simulation via 3 LEDs - red, yellow and green.

## Wiring

```
GPIO17 (11) -> Breadboard (+) -> Resistor (220 Ω) -> Red LED long leg (+, anode)
GPIO10 (19) -> Breadboard (+) -> Resistor (220 Ω) -> Yellow LED long leg (+, anode)
GPIO7  (26) -> Breadboard (+) -> Resistor (220 Ω) -> Green LED long leg (+, anode)
GND    (6)  -> Breadboard (-) -> LED short leg (-, cathode)
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
