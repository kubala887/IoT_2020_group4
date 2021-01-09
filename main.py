#title           :main.py
#description     :Main script for the sensor
#author          :Jakub Kornaś, Piotr Lichosyt
#date            :20201216   
#notes           :Check your RPi pinout befor use!
#==============================================================================


#Libraries
import RPi.GPIO as GPIO
import time
import numpy as np
import configparser

#Modules
import HTTP
import gps
import sms

def setMainGPIOs():
    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)
 
    #set GPIO Pins - sensor 1
    GPIO_TRIGGER = 18
    GPIO_ECHO = 24
    
    #set GPIO Pins - sensor 2
    GPIO_TRIGGER2 = 25
    GPIO_ECHO2 = 23
     
    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
    GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
    GPIO.setup(GPIO_ECHO2, GPIO.IN)



#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins - sensor 1
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#set GPIO Pins - sensor 2
GPIO_TRIGGER2 = 25
GPIO_ECHO2 = 23
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)


#initialize globals
size = 100
binType = 'CITY'
ID = 50
lon = 20.026184
lat = 50.087367
fill = 0
track = 55
timestamp = (int(time.time()))*1000000000

currentDistance = 0
requestUpdateFlag = True

#Function for measuring distance
def distance():
    setMainGPIOs()
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    dis = (TimeElapsed * 34300) / 2
    
    GPIO.cleanup()
    
    
    return dis

def distance2():
    setMainGPIOs()
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER2, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER2, False)
 
    StartTime2 = time.time()
    StopTime2 = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO2) == 0:
        StartTime2 = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO2) == 1:
        StopTime2 = time.time()
 
    # time difference between start and arrival
    TimeElapsed2 = StopTime2 - StartTime2
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    dis2 = (TimeElapsed2 * 34300) / 2
    
    GPIO.cleanup()
    
    return dis2

#Function to categorize the measurement
def distCheck(newDistance,dist,sensorID):
    #expected states
    if dist-1 < newDistance < dist+1:
        setDistance = dist
        return setDistance
        
    if size >= newDistance >= dist+1:
        setDistance = distValidate(newDistance,dist,sensorID);
        return setDistance
        
    if 0 <= newDistance <= dist-1:
        setDistance = distValidate(newDistance,dist,sensorID);
        return setDistance
    #edge cases
    if newDistance > size:
        setDistance = distValidate(newDistance,dist,sensorID);
        return setDistance
        
    if distance < 0:
        setDistance = 0
        return setDistance

        
#Function to validate the measurement
def distValidate(newDistance,dist,sensorID):
    #global validatedDistance
    a = []
    for i in range(7):
        if sensorID == 1:
            a.append(round(distance(),1))
            print("licze srednia dla sens1 poraz: " + str(i) + " odczyt: " + str(a[i]))
            time.sleep(2)
        if sensorID == 2:
            a.append(round(distance2(),1))
            print("licze srednia dla sens2 poraz: " + str(i) + " odczyt: " + str(a[i]))
            time.sleep(2)

    a.remove(max(a))
    a.remove(min(a))

    meanVal = np.mean(a)
    print("srednia: " + str(meanVal))
    stdVal = np.std(a)
    print("odchyl: " + str(stdVal))
    
    if (newDistance-0.6 <= meanVal <= newDistance+0.6) and stdVal <= 2:
        validatedDistance = newDistance
        return validatedDistance
    else:
        validatedDistance = dist
        return validatedDistance

# calculate amount of garbage in %
def calculateFill(fill):
    fill = round(((size-currentDistance)/size)*100,1)
    print("CURRENT FILL: " + str(fill) + "%")

    return fill
    
def setGPSPosition():
    global lon
    global lat
    config = configparser.ConfigParser()
    config.read("position.txt")
    lon = config.get("position", "longitude")
    lat = config.get("position", "latitude")
    #print(float(temp_lon))
    #print(float(temp_lat))
    #lon = round(float(temp_lon),6)
    #lat = round(float(temp_lat),6)

# get GPS position to position.txt and update system time
def getGPSLocation():
    gps.getPosAndSave()
    setGPSPosition()

# push new data through http with LTE (http module)
def requestUpdate(binType,ID,lon,lat,fill,track,timestamp):
    print('UPDATE_PUSH!')
    HTTP.pushData(str(binType),str(ID),str(lon),str(lat),str(fill),str(track),str(timestamp))

# read config data from sms.txt
def setSMSParameters():
    global binType
    global size
    global track
    global ID
    config = configparser.ConfigParser()
    config.read("sms.txt")
    binType = config.get("sms", "binType")
    size = round(float(config.get("sms", "size")),1)
    print(size)
    track = config.get("sms", "track")
    ID = config.get("sms", "ID")

# check for new configurations in sms
def checkSmsInbox():
    sms.readMessages()
    setSMSParameters()

 
if __name__ == '__main__':
    try:
        # read sms configuration for the module
        checkSmsInbox()
        time.sleep(1)
        # get GPS position and sync system time
        getGPSLocation()
        time.sleep(1)

        # initial distances from sensors
        dist = round(distance(),1)
        time.sleep(1.5)
        dist2 = round(distance2(),1)
        time.sleep(1.5)
        print ("Measured Initial Distance from sensor 1 = " + str(dist))
        print ("Measured Initial Distance from sensor 2 = " + str(dist2))


        while True:
            # mdist- measured distance with distance function - take measurements:
            mdist = round(distance(),1)
            print(mdist)
            time.sleep(1.5)
            mdist2 = round(distance2(),1)
            print(mdist2)
            time.sleep(1.5)

            # check if both measurements seem real
            print("robie tempdist1 check")
            tempDistance = distCheck(mdist,dist,1)
            print("robie tempdist2 check")
            tempDistance2 = distCheck(mdist2,dist2,2)
            print("koniec obu checkow")

            #if measurement legit and differ then update it
            if tempDistance != dist:
                dist = tempDistance
                print("New Measured Distance from sensor 1= " + str(dist))
                requestUpdateFlag = True


            if tempDistance2 != dist2:
                dist2 = tempDistance2
                print("New Measured Distance from sensor 2= " + str(dist2))
                requestUpdateFlag = True

            # if fill changed choose actual measurement, calculate fill, push data to DB
            if requestUpdateFlag:
                if dist > dist2:
                    currentDistance = dist2
                else:
                    currentDistance = dist

                fill = calculateFill(currentDistance);

                #TODO: add try/catch !
                timestamp = (int(time.time()))*1000000000
                requestUpdate(binType,ID,lon,lat,fill,track,timestamp)
                #getGPSLocation()
                requestUpdateFlag = False
            
            # erase the need of update before next loop
            
            print("petla glowna wykonana")
            time.sleep(5)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Stopped by user (ctrl+c or different)")
        GPIO.cleanup()