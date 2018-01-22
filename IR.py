import wiringpi



class IRBeamBreaker(object):


    def __init__(self, input_BCM_pin):

        wiringpi.wiringPiSetupGpio()
        self.photo_diode_input_pin = input_BCM_pin
        wiringpi.pinMode(input_BCM_pin, wiringpi.GPIO.INPUT)
        wiringpi.pullUpDnControl(input_BCM_pin, wiringpi.PUD_UP)


    def isBeamBroken(self):
        return wiringpi.digitalRead(self.photo_diode_input_pin)
