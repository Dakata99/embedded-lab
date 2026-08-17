# Web client for monitoring temperature and humidity

## How to?

Firstly, setup the environment:
```bash
. setupenv
```

then run:
```bash
flask --app aht10/user-space/web.py run -h $(hostname -I)
```

Use `--debug` option to enable reloading (while developing).
