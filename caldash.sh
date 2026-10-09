#!/bin/bash

cd CalendarDashboard
VENV_PYTHON="/home/grunkies/CalendarDashboard/.venv/bin/python3.13"
export DISPLAY=:0
export XAUTHORITY=/home/grunkies/.Xauthority
$VENV_PYTHON src/script.py

# source .venv/bin/activate
# /usr/bin/python3.13 script.py
