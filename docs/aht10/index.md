# AHT10 - temperature and humidy sensor

## Wiring

```
3V3   (1) -> Breadboard (+)      -> VIN
GPIO2 (3) -> Breadboard (x1, y1) -> SDA
GPIO3 (5) -> Breadboard (x2, y2) -> SCL
GND   (6) -> Breadboard (-)      -> GND
```

where `(x1, y1)` and `(x2, y2)` are a row from `1` to `30` and a column for `a` to `j`.

## How to detect the sensor?

Firstly, run:
```bash
sudo rasp-config
```
then enable I2C by `Interface Options → I2C → Enable`.

When enabled, restart the Raspberry PI:
```bash
sudo reboot
```

When device is rebooted, run:
```bash
sudo apt update
sudo apt install -y i2c-tools
```

Check that the I2C device exists by:
```bash
ls /dev/i2c*
```
Expected output is `/dev/i2c-1`.

To scan the I2C bus, run:
```bash
sudo i2cdetect -y 1
```

Expected output is:
```bash
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- 38 -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```
