import wiringpi
from time import sleep

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(24, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(24, wiringpi.PUD_DOWN)

while True:
	if wiringpi.digitalRead(24) == 1:
		print "==========="
	elif wiringpi.digitalRead(24) == 0:
		print " "
	sleep(0.01)
