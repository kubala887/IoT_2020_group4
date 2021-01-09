# -*- coding:utf-8 -*-
#title           :gps.py
#description     :Script for getting coordinates and time from GPS
#author          :Damian Piasecki
#date            :20201216   
#==============================================================================


import RPi.GPIO as GPIO

import serial
import time
import os
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
        return 0

def get_gps_position():
    rec_null = True
    info_answer = 0
    session_answer = 0
    print('Start GPS session...')
    rec_buff = ''
    while 0 == session_answer:
        session_answer = send_at('AT+CGNSPWR=1','OK',1)
        if ',,,,,,' in rec_buff:
            print('GPS is still not ready ...')
            rec_null = False
            time.sleep(60)
    info_answer = send_at('AT+CGNSINF','+CGNSINF: ',1)
    if 1 == info_answer:
        info_answer = 0
        global latitude
        global longitude
        global date_str
        date_str = data[2]
        latitude = data[3]
        longitude = data[4]
        print('Latitiude: ' + latitude)
        print('Longitude: ' + longitude)
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
    time.sleep(2)
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
    file.write('[position]' + '\n')
    file.write('latitude = ' + latitude + '\n')
    file.write('longitude = ' + longitude + '\n') 
    file.close()

def set_date(date_str):
    try:
        date_str = date_str.split(".")
        date = date_str[0]
        date = date[0:4] + '/' + date[4:6] + '/' + date[6:8] + ' ' + date[8:10] + ':' + date[10:12] + ':' + date[12:14]
        print('Time: '+ date)
        command = 'sudo date +%Y%m%d%H%M%S -s "{}" -u'.format(date)
        os.system(command)
    except:
        print("Cannot set time and date")

def getPosAndSave():
    try:
        ser = serial.Serial('/dev/ttyS0',115200)
        ser.flushInput()

        power_key = 4
        rec_buff = ''
        rec_buff2 = ''
        time_count = 0
        
        power_on(power_key)
        get_gps_position()
        save_position(latitude,longitude)
        set_date(date_str)
        power_down(power_key)
    except:
        if ser != None:
            ser.close()
        power_down(power_key)
        GPIO.cleanup()
    if ser != None:
            ser.close()
            GPIO.cleanup()

