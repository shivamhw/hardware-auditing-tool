#!/bin/bash

command="flashrom -p linux_spi:dev=/dev/spidev0.0,spispeed="
speed="8000"

if [[ $# -eq 1 ]]; then
    speed=$1
elif [[ $# -gt 1 ]]; then
    echo "error"
    exit
fi

command=$command$speed
device_list=`$command -r /home/pi/firm/test.bin`
if [[ $device_list == *"Reading flash... done."* ]]; then
    echo "success reading flash"
else
    echo "failed dump"
fi

