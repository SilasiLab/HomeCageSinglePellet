import wiringpi
from time import sleep



# Initializes wiringpi and sets pins to BCM pin numbering.
# Note: Must be called before using any other function in this module.
def initGPIO():

    wiringpi.wiringPiSetupGpio()


# This function is a wrapper around the wiringPi functions used
# in configuring a GPIO pin for digital read or write.
#
# Note: The pins are initialized to the BCM numbering scheme.
# Provide the BCM_pin_number and IO_flag(1 or 0) for input or 
# output respectively.
def configureGPIOPin(BCM_pin_number, IO_flag):
            
    if IO_flag == 1:
        wiringpi.pinMode(BCM_pin_number, wiringpi.GPIO.INPUT)
    elif IO_flag == 0:
        wiringpi.pinMode(BCM_pin_number, wiringpi.GPIO.OUTPUT)
                                                

    #TODO: Figure out exactly what the PUD resistors do and update this comment
    # to properly explain what it does.
    wiringpi.pullUpDnControl(BCM_pin_number, wiringpi.PUD_DOWN)
                                                        

# This function polls the supplied BCM GPIO pin
# for it's state every <polling_rate_ms> milliseconds.
def listenToPinInput(BCM_pin_number, polling_rate_ms):
                                                                
    pin_state = 0

    while True: 

        pin_state = wiringpi.digitalRead(BCM_pin_number)

        # Sleep to slow polling to avoid eating all CPU cycles
        sleep(float(polling_rate_ms)/1000.0)


def getPinState(BCM_pin_number):
	return wiringpi.digitalRead(BCM_pin_number)
