#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)
ser.flushInput()

power_key = 5
rec_buff = ''


def power_on(power_key):
    print('SIM7600X is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key, GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(2)
    ser.flushInput()
    print('SIM7600X is ready')


def power_down(power_key):
    print('SIM7600X is loging off:')
    GPIO.output(power_key, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key, GPIO.LOW)
    time.sleep(2)
    print('Good bye')


def send_at(command, back, timeout):
    rec_buff = ''
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.1)
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
            return 1
    else:
        print(command + ' no responce')


try:
    power_on(power_key)

    send_at('AT+CSQ', 'OK', 1)  # signal quality report
    send_at('AT+CPSI?', 'OK', 1)  # Inquiring UE system information
    send_at('AT+CMGF=1', 'OK', 1)  # txt format of message
    send_at('AT+CPMS="SM","SM","SM"', 'OK', 1)  # messages to be read from SIM message storage
    send_at('AT+CMGL="ALL"', 'OK', 1)  # retrieving all sms messages

    file = open("data.txt", "w")
    file.write(data + '\n')
    file.close()

    with open('data.txt') as fd:
        text = fd.read()  # str
        lines = text.split('\n')[::-1]  # lista wszystkich lini z tekstu (ale od końca)
        for line in lines:
            if 'type' in line:  # linia ze słowem 'type' ostatni z pliku np.: type: type1, size: 176, routeID: 2
                values = line.split(',')  # linia zamieniona na liste: ['type: type1', ' size: 176', ' routeID: 2']
                new_text = ''

                for value in values:
                    try:
                        k, v = value.split(':')  # ['type', ' type1']
                        k = k.strip()  # 'type'
                        v = v.strip()  # 'type1'
                        if k == 'type':
                            v = "'" + v + "'"  # 'type1'
                        elif v in ['', ' ']:  # sprawdzamy parametry inne niż 'type'; 
                            v = '0'
                        new_value = k + ' = ' + v + '\n'
                        new_text = new_text + new_value
                        with open('sms.txt', 'w') as fd_w:
                            fd_w.write(new_text)
                    except Exception:
                        pass
                break

    power_down(power_key)

except:
    if ser != None:
        ser.close()
        GPIO.cleanup()

if ser != None:
    ser.close()
    GPIO.cleanup()

