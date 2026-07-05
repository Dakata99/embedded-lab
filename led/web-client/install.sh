#!/bin/bash

if [[ $(which pyinstaller) == "" ]]; then
    echo "pyinstaller is not installed. Please install it first."
    exit 1
fi

NAME=led-web-client
APP=web.py

# Make sure the dist directory does not exist
rm -rf /tmp/dist-$NAME

# Install the bundle
pyinstaller \
    --clean \
    --onedir \
    --name $NAME \
    --hidden-import gpiozero.pins.lgpio \
    --hidden-import lgpio \
    $APP \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --add-data "config.json:." \
    --distpath /tmp/dist-$NAME

# Install the bundle to /opt/
sudo rm -rf /opt/$NAME
sudo cp -r /tmp/dist-$NAME /opt/$NAME

sudo tee /etc/systemd/system/$NAME.service > /dev/null << EOF
[Unit]
Description=LED Web Client
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=rpidev

RuntimeDirectory=$NAME
RuntimeDirectoryMode=0755
WorkingDirectory=/run/$NAME

Environment="LED_CONFIG=/opt/$NAME/$NAME/_internal/config.json"

ExecStart=/bin/sh -c 'export HOSTIP="$(hostname -I)"; exec /opt/$NAME/$NAME/$NAME'

Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Install it as a service
sudo systemctl daemon-reload
sudo systemctl enable --now $NAME.service
sudo systemctl restart $NAME.service
sudo systemctl status $NAME.service
