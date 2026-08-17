#!/bin/bash

if [[ $(which pyinstaller) == "" ]]; then
    echo "pyinstaller is not installed. Please install it first."
    exit 1
fi

NAME=aht10-web
APP=web.py
DIST=/tmp/dist-$NAME
DEST=/opt/$NAME

# Make sure the dist directory does not exist
rm -rf $DIST

# Install the bundle
pyinstaller \
    --clean \
    --onedir \
    --name $NAME \
    $APP \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --distpath $DIST

# Install the bundle to /opt/
sudo rm -rf $DEST
sudo cp -r $DIST $DEST

sudo tee /etc/systemd/system/$NAME.service > /dev/null << EOF
[Unit]
Description=AHT10 Flask Web Dashboard
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=rpidev

RuntimeDirectory=$NAME
RuntimeDirectoryMode=0755
WorkingDirectory=/run/$NAME

ExecStart=/bin/sh -c 'export HOSTIP="$(hostname -I)" && exec $DEST/$NAME/$NAME'

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
