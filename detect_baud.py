from time import time
import serial
import RPi.GPIO as GPIO
import sys
from time import sleep, time
from os import remove

relay_pin = 26 
baudrates = [9600, 115200, 4800]
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
output_file = "baud_output"
def check_baud_output(baud_rate, delay, power_delay):
# turn off board
    GPIO.output(relay_pin, GPIO.LOW)
    sleep(power_delay)
# change baud 
    ser = serial.Serial("/dev/ttyS0", baud_rate)
# turn on board 
    GPIO.output(relay_pin, GPIO.HIGH)
# for a perticular time frame
    start = time()
    output = f"\n\nUSING {baud_rate} ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n"
    while(True):
        end = time()
        received_data = ser.read()              #read serial port
        sleep(0.03)
        data_left = ser.inWaiting()
        received_data += ser.read(data_left)
        try:
            print (received_data.decode("ascii"))
            output += received_data.decode("ascii")
        except:
            pass  
        if(end - start > delay): 
            break
    with open(output_file, "a+") as f:
        f.write(output)

def main(sampling_time, power_cycle_delay):
    try:
        remove(output_file)
    except:
        pass
    for rate in baudrates:
        check_baud_output(rate, int(sampling_time), int(power_cycle_delay))

# main()