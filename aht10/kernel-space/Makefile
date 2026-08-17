NAME := aht10-lab

obj-m += $(NAME).o

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD  := $(shell pwd)
OUT  ?= $(PWD)/build

all:
	$(MAKE) -C $(KDIR) M=$(PWD) MO=$(OUT) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) MO=$(OUT) clean
	rm -rf $(OUT)

dts:
	dtc -@ -I dts -O dtb -o $(NAME).dtbo $(NAME)-overlay.dts
