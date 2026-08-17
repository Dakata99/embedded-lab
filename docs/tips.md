# Tips

## How to detect your Raspberry Pi?

```bash
nmap -p <PORT> --open <NETWORK_IP>/<MASK>
```

## How to serve documentation from Raspberry PI to PC?

Firstly, get the IP of your Raspberry PI by:
```bash
hostname -I
```

Run the following command:
```bash
uv run mkdocs serve -a <IP>:8000
```

or in one line:
```bash
uv run mkdocs serve -a $(hostname -I | cut -d' ' -f1):8000
```

Then open a browser on your PC and enter: `http://<IP>:8000` or get it via:
```bash
echo "https://$(hostname -I | cut -d ' ' -f1):8000"
```

## How to run Flask?

Firstly, setup the environment:
```bash
. setupenv
```

and then:
```bash
flask --app /path/to/app.py run -h $(hostname -I)
```

Use `--debug` option to enable reloading (while developing).

Then open a browser on your PC and enter: `http://<IP>:5000`, where `<IP>=$(hostname -I)` or get it via: 
```bash
echo "https://$(hostname -I | cut -d ' ' -f1):5000"
```
