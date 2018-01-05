import wiringpi
from time import sleep

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(23, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(23, wiringpi.PUD_DOWN)

while True:
	if wiringpi.digitalRead(23) == 1:
		print "==========="
	elif wiringpi.digitalRead(23) == 0:
		print " "
	sleep(0.01)
