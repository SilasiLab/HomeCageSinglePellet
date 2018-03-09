import wiringpi



class IRBeamBreaker(object):


    def __init__(self, input_BCM_pin):

        # This initializes the Pi's GPIO pins for wiringPi with the BCM pin numbering scheme.
        wiringpi.wiringPiSetupGpio()

        # This block sets the pin that will be used to read the state of the IR photodiode to input mode
        # and sets the pin's pullUpDn resistor to PULL_UP. I don't understand exactly what that means but
        # the IR beam breaker won't work without it.
        self.photo_diode_input_pin = input_BCM_pin
        wiringpi.pinMode(input_BCM_pin, wiringpi.GPIO.INPUT)
        wiringpi.pullUpDnControl(input_BCM_pin, wiringpi.PUD_UP)


    # This function returns the state of the IR photodiode, which represents
    # the IR beam being broken or unbroken.
    def getBeamState(self):
        return wiringpi.digitalRead(self.photo_diode_input_pin)
