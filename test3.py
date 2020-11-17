#Libraries
import RPi.GPIO as GPIO
import time

import numpy as np
 
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

#globals
size = 100.0
currentDistance = 0
routeID = 0

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

def distance2():
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
	distance2 = (TimeElapsed2 * 34300) / 2
 
	return distance2

#Function to categorize the measurement
def distCheck(newDistance,dist,sensorID):
	#expected states
	#global setDistance
	if dist-1 < newDistance < dist+1:
		setDistance = dist
		
	if size >= newDistance >= dist+1:
		setDistance = distValidate(newDistance,dist,sensorID);
		
	if 0 <= newDistance <= dist-1:
		setDistance = distValidate(newDistance,dist,sensorID);
	#edge cases
	if size + 3 >= newDistance > size:
		setDistance = size
		
	if distance < 0:
		setDistance = 0

	return setDistance
		
#Function to validate the measurement
def distValidate(newDistance,dist,sensorID):
	#global validatedDistance
	a = []
	for i in range(10):
		if sensorID == 1:
			a.append(round(distance(),1))
			time.sleep(0.5)
		if sensorID == 2:
			a.append(round(distance2(),1))
			time.sleep(0.5)

	meanVal = np.mean(a)
	stdVal = np.std(a)
	
	if newDistance-0.5 <= meanVal <= newDistance+0.5 and stdVal <= 1:
		validatedDistance = newDistance
	else:
		validatedDistance = dist

	return validatedDistance


 
if __name__ == '__main__':
	try:
		dist = round(distance(),1)
		time.sleep(0.1)
		dist2 = round(distance2(),1)
		time.sleep(0.1)
		print ("Measured Initial Distance from sensor 1 = " + str(dist))
		print ("Measured Initial Distance from sensor 2 = " + str(dist2))
		time.sleep(0.1)
		while True:
			# mdist- measured distance with distance function - take measurements:
			mdist = round(distance(),1)
			time.sleep(0.1)
			mdist2 = round(distance2(),1)

			# check if both measurements seem real
			tempDistance = distCheck(mdist,dist,1)
			tempDistance2 = distCheck(mdist2,dist2,2)

			#if measurement legit and differ then update it
			if tempDistance != dist:
				dist = tempDistance
				print("New Measured Distance from sensor 1= " + str(dist))


			if tempDistance2 != dist2:
				dist2 = tempDistance2
				print("New Measured Distance from sensor 2= " + str(dist2))

			# choose actual measurement and calculate fill
			if dist > dist2:
				currentDistance = dist2
			else:
				currentDistance = dist

			fill = round(((size-currentDistance)/size)*100,1)
			print("CURRENT FILL: " + str(fill) + "%")

			time.sleep(3)
 
		# Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Stopped by user (ctrl+c or different)")
		GPIO.cleanup()