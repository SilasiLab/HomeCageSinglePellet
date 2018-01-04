import wiringpi
from time import sleep

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(23, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(23, wiringpi.PUD_DOWN)

while True:
	print wiringpi.digitalRead(23)
	sleep(0.01)
