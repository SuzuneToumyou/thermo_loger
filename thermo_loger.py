#!/usr/bin/python3
# -*- coding: utf-8 -*

import pigpio
import time
#import struct

import math
import csv
import sys

import datetime

THERMO_HEAT = 85

import RPi.GPIO as GPIO

PORT_1 = 26

sleep_time = 20

def io_port_on():
    GPIO.output(PORT_1, GPIO.HIGH)

def io_port_off():
    GPIO.output(PORT_1, GPIO.LOW)

def senser_get(pass_datatmp):
    heat_flag = 0
    pi = pigpio.pi()
    addr = 0x0a
    try:
        h = pi.i2c_open(1,addr) # ハンドル取得
        pi.i2c_write_device(h, [0x4d])
        time.sleep(2)
        count, result = pi.i2c_read_device(h,2051)
        time.sleep(2)
    except:
        count = -80
    if count <= 0:
        return(0)

    else:
        now_date = datetime.datetime.now()
        now = now_date.strftime("%Y%m%d%H%M%S")

        tP = []

        readbuff = bytes(result)

        tPTAT = (256*readbuff[1] + readbuff[0])/10

        for i in range(1025):
            if i != 0:
                tmp = (256*readbuff[i*2+1] + readbuff[i*2])/10
                if (tmp >= THERMO_HEAT):
                    heat_flag = 1
                tP.append([tmp, (i-1)%32, math.floor((i-1)/32)])

        if heat_flag == 1:
            io_port_on()

            file_name= "./" + pass_datatmp + "/" + str(now) + ".csv"
            fout= open(file_name,"w")
            writer = csv.writer(fout)
            writer.writerows(tP)
            fout.close()
        else :
            io_port_off()

        return(1)
    tP.clear()
    pi.i2c_close(h)

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PORT_1, GPIO.OUT)

    if(len(sys.argv) <= 1):
        pass_data = "datalog"
    else:
        pass_data = sys.argv[1]
    try:
        while True:
            return_data = senser_get(pass_data)
            if return_data == 0:
                num = 0
                while return_data == 0 or num <= 3:
                    return_data = senser_get(pass_data)
                    num = num + 1
            time.sleep(sleep_time)

    finally:
        GPIO.cleanup()
