#!/bin/bash

PI_HOST="pi@172.30.168.192"
PYTHON_PATH="/home/pi/upload_individual.py"

# SSH into the Pi and run the script
ssh "$PI_HOST" "python $PYTHON_PATH"
