# LED

The `led` folder contains 3 Python scripts that:

- control a LED via some commands
- simulate a traffic light via 3 LEDs
- web client for controllig the 3 LEDs

Male-female jumper wires may be needed.

## How to manually control a LED?

Suppose the following wiring is made:
```
GPIO18 (12) -> Breadboard (+) -> Resistor (220 Ω) -> LED long leg (+, anode)
GND    (14) -> Breadboard (-) -> LED short leg (-, cathode)
```

When the pin is HIGH (`dh`), the LED lights. When it is LOW (`dl`), the LED turns off.

Turn on the LED:
```bash
pinctrl set <GPIO> op dh
```

and to turn off:
```bash
pinctrl set <GPIO> op dl
```

To get the state of the GPIO pin, run:
```bash
pinctrl get <GPIO>
```

To reset the GPIO pin state, run:
```bash
pinctrl set <GPIO> no
```

## Tips

- Use `pinout` command to check the schema of the GPIO pins. Or visit [pinout.xyz](https://pinout.xyz/).
- Do not connect an LED directly to a GPIO pin without a resistor. The resistor limits current. Think of it as a small speed limit for electricity.
- The long LED leg is usually the positive side, called anode. The short LED leg is usually the negative side, called cathode, and goes to GND.
