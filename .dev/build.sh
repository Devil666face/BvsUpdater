#!/bin/bash
./venv/bin/python -m nuitka \
--onefile \
--standalone \
--follow-imports \
--include-plugin-directory=./venv/lib/python3.10/site-packages/apscheduler \
main.py
ARCHIVE_NAME="${PWD##*/}.tgz"
tar -cvzf $ARCHIVE_NAME main.bin drw/ ksc/ script/ updater.yaml bvsupdater.service .env.sample init.sh
# XZ_OPT=-e9T0 tar cJf $ARCHIVE_NAME main.bin drw/ ksc/ script/ updater.yaml bvsupdater.service .env.sample init.sh
mkdir -p ./dist && mv $ARCHIVE_NAME ./dist