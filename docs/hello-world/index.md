# Hello world "driver"

This is an example of how to load/unload a driver into the kernel. It's not a real driver, but a simulation.

## How to?

Firstly, compile the "driver" by:
```bash
make
```

Then install it in the kernel:
```bash
sudo insmod hello-world.ko
```

To verify that it is loaded by the kernel, run:
```bash
dmesg | tail
```
and look for your output message from the `__init hello_init` function (in this case: `Hello, World!`)

To remove/unload it, run:
```bash
sudo rmmod hello_world
```
and check for your output message from the `__exit hello_exit` function (in this case: `Goodbye, World!`) with:
```bash
dmesg | tail
```

To clean up, run:
```bash
make clean
```
