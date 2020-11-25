#!/usr/bin/python
# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO

import serial
import time
from datetime import datetime


ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

power_key = 4
rec_buff = ''
rec_buff2 = ''
time_count = 0


def send_at(command,back,timeout):
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01 )
        rec_buff = ser.read(ser.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
            print(command + ' ERROR')
            print(command + ' back:\t' + rec_buff.decode())
            return 0
        else:
            print(rec_buff.decode())
            global data
            data = rec_buff.decode()
            data = data.split(",")
            return 1
    else:
        print('GPS is not ready')
        return 0

def get_gps_position():
    rec_null = True
    answer = 0
    print('Start GPS session...')
    rec_buff = ''
    send_at('AT+CGNSPWR=1','OK',1)
    time.sleep(2)
    answer = send_at('AT+CGNSINF','+CGNSINF: ',1)
    if 1 == answer:
        answer = 0
        if ',,,,,,' in rec_buff:
            print('GPS is not ready')
            rec_null = False
            time.sleep(1)
        else:
            global latitude
            global longitude
            global date_str
            date_str = data[2]
            latitude = data[3]
            longitude = data[4]
            print("Time: %s", date_str)
            print("Latitiude: %s", latitude)
            print("Longitude: %s", longitude)
    else:
        print('error %d'%answer)
        rec_buff = ''
        send_at('AT+CGPS=0','OK',1)
        return False
    time.sleep(1.5)

def power_on(power_key):
    print('SIM7600X is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)
    ser.flushInput()
    time.sleep(60)
    print('SIM7600X is ready')

def power_down(power_key):
    print('SIM7600X is loging off:')
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)
    print('Good bye')

def save_position(latitude,longitude):
    file = open("position.txt","w")
    file.write(latitude + '\n')
    file.write(longitude + '\n') 
    file.close()

def save_date(date_str):
    print(date_str)
    date_str = date_str.split(".")
    print(date_str)
    date = date_str[0]
    date = date[0:4] + '/' + date[4:6] + '/' + date[6:8] + ' ' + date[8:10] + ':' + date[10:12] + ':' + date[12:14]
    # print(date)
    file = open("time.txt","w")
    file.write(date + "\n")
    file.close()
try:
    power_on(power_key)
    get_gps_position()
    save_position(latitude,longitude)
    save_date(date_str)
    power_down(power_key)
except:
    if ser != None:
        ser.close()
    power_down(power_key)
    GPIO.cleanup()
if ser != None:
        ser.close()
        GPIO.cleanup()  


