# Web client for LED control

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
