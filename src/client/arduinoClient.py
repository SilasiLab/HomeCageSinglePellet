"""
    Author: Julian Pitney
    Email: JulianPitney@gmail.com
    Organization: University of Ottawa (Silasi Lab)
"""


import serial
from time import sleep

class client(object):


    def __init__(self, arduinoSerialPortPath, baudrate):

        # Open serial connection with periphral board (Note: Arduino will reset
        #   when you open a serial connection with it, so a ~3 second delay
        #   after opening the connection is recommended)
        self.serialInterface = serial.Serial(arduinoSerialPortPath, baudrate)
        
        self.serialInterface.flushInput()
        sleep(3)
        # Wait for Arduino to say it's ready TODO: readline is blocking....add timeout eventually
        readyMsg = self.serialInterface.readline()
        print(".....ok?")
        if readyMsg == b"READY\n":
            print("Arduino: ", readyMsg)
        else:
            print("Arduino took too long to respond...shutting down")
            exit()


    # DEPRECATED: This function was used to read RFIDs from the Arduino, before we switched the 
    # RFID reader from the Arduino to the PC. 
    def listenForRFID(self):

        RFID = self.serialInterface.readline().rstrip().decode()
        self.serialInterface.flushInput()
        return RFID

