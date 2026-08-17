# Linux kernel driver

## Datasheet

The notes below, describe the full measurement cycle:
```
1. Power-on delay
   - After power is applied, wait up to 20 ms before sending commands.

2. Initialization
   - Send initialization command:
     0xE1 0x08 0x00

3. Trigger measurement
   - Send:
     0xAC 0x33 0x00

4. Wait for conversion
   - Wait at least 75 ms.

5. Read payload
   - Read 6 bytes from the sensor.

6. Check status
   - byte[0] is the status byte.
   - bit 7 = busy flag.
   - bit 3 = calibration flag.

7. Extract raw humidity and temperature
   - Humidity is a 20-bit value.
   - Temperature is a 20-bit value.

8. Convert raw values
   - RH = humidity_raw / 2^20 * 100
   - T  = temperature_raw / 2^20 * 200 - 50
```

## Hardware wiring

## Device Tree overlay

## Kernel module build/install

To build the kernel driver do:
```bash
cd aht10/kernel-space
make
```
and to insall it:
```bash
sudo insmod build/aht10-lab.ko
```

## hwmon sysfs paths

## Flask setup

## systemd service



To create the `systemd` service, do:
```bash
sudo vim /etc/systemd/system/aht10-web.service
```

## Troubleshooting
