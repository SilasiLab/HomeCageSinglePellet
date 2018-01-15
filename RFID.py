import serial
import wiringpi 
from time import sleep


class RFID_Reader(object):
    
    def __init__(self, serial_interface_path, baudrate, proximity_pin_BCM_number):

        self.serial_interface = serial.Serial(serial_interface_path, baudrate)
        self.proximity_pin_BCM_number = proximity_pin_BCM_number

        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(proximity_pin_BCM_number, wiringpi.GPIO.INPUT)
        wiringpi.pullUpDnControl(proximity_pin_BCM_number, wiringpi.PUD_DOWN)


    def readByte():
        return self.serial_interface.read()


    def readProximityState():
        return wiringpi.digitalRead(self.proximity_pin_BCM_number)


    def listenForRFID():

        RFID_code = []
        byte = ''

        while byte != '\r':
            byte = self.readByte()
            RFID_code.append(byte)

        self.serial_interface.reset_input_buffer()
        sleep(1)
        
        return ''.join(RFID_code[2:])