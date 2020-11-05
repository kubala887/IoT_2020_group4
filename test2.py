#Libraries
import RPi.GPIO as GPIO
import time

import numpy as np
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#globals
size = 100.0

#Function for measuring distance
def distance():
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
	distance = (TimeElapsed * 34300) / 2
 
	return distance

#Function to categorize the measurement
def distCheck(newDistance,dist):
	#expected states
	if dist-1 < newDistance < dist+1:
		setDistance = dist
		
	if size >= newDistance >= dist+1:
		setDistance = distValidate(newDistance,dist);
		
	if 0 <= newDistance <= dist-1:
		setDistance = distValidate(newDistance,dist);
	#edge cases
	if size + 3 >= newDistance > size:
		setDistance = size
		
	if distance < 0:
		setDistance = 0
	
	return setDistance
		
#Function to validate the measurement
def distValidate(newDistance,dist):
	a = []
	for i in range(10):
		a.append(round(distance(),1))
	
	meanVal = np.mean(a)
	stdVal = np.std(a)
	
	if newDistance-0.5 <= meanVal <= newDistance+0.5 and stdVal <= 0.5:
		validatedDistance = newDistance
	else:
		validatedDistance = dist

	return validatedDistance
 
if __name__ == '__main__':
	try:
		dist = round(distance(),1)
		print ("Measured Initial Distance = " + str(dist))
		time.sleep(0.1)
		while True:
			dist2 = round(distance(),1)
			tempDistance = distCheck(dist2,dist)
			if tempDistance != dist:
				dist = tempDistance
			print ("New Measured Distance = " + str(dist))    
			time.sleep(1)
 
		# Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Stopped by user (ctrl+c or different)")
		GPIO.cleanup()