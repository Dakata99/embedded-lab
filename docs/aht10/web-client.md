# Web client for monitoring temperature and humidity

## How to?

Firstly, setup the environment:
```bash
uv sync
source .venv/bin/activate
```

then run:
```bash
flask --app aht10/web.py run --host $(hostname -I | cut -d' ' -f 1)
```

Use `--debug` option to enable reloading (while developing).
