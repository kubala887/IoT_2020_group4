#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

power_key = 6
rec_buff = ''
APN = 'CMNET'
ServerIP = '18.134.93.173'
Port = '8086'
Message = 'Waveshare'
data = 'measures,type="KRAKOW" ID="111",long=19.888,lat=50.058,fill=96.87,track="1" 1434067467000000202'
cmd='AT+HTTPDATA='+str(len(data))+',3500'

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
    print('SIM7600X is ready')

def power_down(power_key):
    print('SIM7600X is loging off:')
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)
    print('Good bye')
    
def send_at(command,back,timeout):
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.1 )
		rec_buff = ser.read(ser.inWaiting())
	if rec_buff != '':
		print(rec_buff.decode())
		return 1
	else:
		print(command + ' no responce')


try:
    power_on(power_key)
        
    send_at('AT+CSQ','OK',1)
    send_at('AT+CREG?','OK',1)
    send_at('AT+CPSI?','OK',1)
    send_at('AT+CIPSHUT','OK',1)
    send_at('AT+CGATT=1','OK',1)
    send_at('AT+SAPBR=3,1,"CONTYPE","GPRS"','OK',1)
    send_at('AT+SAPBR=3,1,"APN","internet"','OK',1)
    send_at('AT+CSTT="internet"','OK',1)
    send_at('AT+CIICR','OK',1)
    send_at('AT+HTTPINIT','OK',1)
    time.sleep(3)
    send_at('AT+HTTPPARA="CID",1','OK',1)
    send_at('AT+HTTPPARA="URL","http://18.134.93.173:8086/write?db=projekt_IoT"','OK',1)
    send_at('AT+HTTPPARA="CONTENT","data/binary"','OK',1)
    send_at(cmd,'DOWNLOAD',1) 
    ser.write(data.encode())
    send_at('AT+HTTPACTION=1','',1)
    send_at('AT+HTTPHEAD','',1)
    send_at('AT+HTTPTERM','OK',1)
    power_down(power_key)

   

except:
    if ser != None:
        ser.close()
        GPIO.cleanup()

if ser != None:
        ser.close()
        GPIO.cleanup()
