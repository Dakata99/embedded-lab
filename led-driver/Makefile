obj-m += leds.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean

compile-dtb:
	dtc -@ -I dts -O dtb -o pi-led.dtbo leds-overlay.dts
