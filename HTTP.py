#!/usr/bin/python
 
import RPi.GPIO as GPIO
import serial
import time
 
ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()
 
power_key = 6
rec_buff = ''
type="CITY"
ID="111"
long="19.888"
lat="50.058"
fill="96.87"
track="1"
timestamp="1400000000000000000"
data_measures=',type="'+type+'" ID="'+ID+'",long='+long+',lat='+lat+',fill='+fill+',track='+track+' '+timestamp'
data='measures'+data_measures
#data = 'measures,type="KRAKOW" ID="111",long=19.888,lat=50.058,fill=96.87,track="1" 1434067467000000202'
#data = 'measures,type="CITY" ID="666",long=45.888,lat=50.058,fill=96.87,track="1" 1400000000000000000'
data_binary=data.encode()
cmd='AT+HTTPDATA='+str(len(data))+',2000'
print(cmd)
 
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
    send_at('AT+CIPSHUT','OK',1)
    send_at('AT+CGATT=1','OK',1)
    send_at('AT+SAPBR=3,1,"CONTYPE","GPRS"','OK',1)
    send_at('AT+SAPBR=3,1,"APN","internet"','OK',1)
    send_at('AT+CSTT="internet"','',1)
    time.sleep(3)
    send_at('AT+SAPBR=1,1','',1)
    send_at('AT+CIICR','OK',1)
    send_at('AT+HTTPTERM','OK',1)
    time.sleep(1)
    send_at('AT+HTTPINIT','OK',1)
    time.sleep(1) 
    send_at('AT+HTTPPARA="CID",1','OK',1)
    send_at('AT+HTTPPARA="URL","http://18.134.93.173:8086/write?db=projekt_IoT"','OK',1)
    send_at('AT+HTTPPARA="CONTENT","data/binary"','OK',1)
    send_at(cmd,'DOWNLOAD',1)
    time.sleep(1)
    ser.write(data.encode())
    print('write finished')
    time.sleep(1)
    send_at('AT+HTTPACTION=1','',3)
    send_at('AT+HTTPHEAD','',3)
    send_at('AT+HTTPTERM','OK',1)
    power_down(power_key)
 
 
 
except:
    if ser != None:
        ser.close()
        GPIO.cleanup()
 
if ser != None:
        ser.close()
        GPIO.cleanup()

