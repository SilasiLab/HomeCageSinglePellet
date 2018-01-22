import wiringpi



class IRBeamBreaker(object):


    def __init__(self, input_BCM_pin):

        wiringpi.wiringPiSetupGPIO()
        self.photo_diode_input_pin = input_BCM_pin
        wiringpi.pinMode(input_BCM_pin, wiringpi.GPIO.INPUT)
        wiringpi.pullUpDnControl(input_BCM_pin, wiringpi.PUD_UP)


    # This function returns 1 if the IR beam is broken and 0 otherwise.
    # The return value is always the opposite of the photo_diode_input_pin's
    # value.
    def isBeamBroken(self):
        return !wiringpi.digitalRead(self.photo_diode_input_pin)
