#!/usr/bin/env bash

dir="$(dirname "$0")"
cd "$dir"

sudo systemctl restart bluetooth
./venv/bin/python main.py
