"""
    Author: Julian Pitney
    Email: JulianPitney@gmail.com
    Organization: University of Ottawa (Silasi Lab)
"""

import os

def gen_profile(mouseName):

    if(os.path.isdir("../../AnimalProfiles/" + str(mouseName))):
        print(mouseName + " already has a profile! Skipping profile creation...")
        return 0
    else:
        print("Creating profile for " + str(mouseName) + "...")

    RFID = input("Enter animal RFID: ")
    cageNumber = input("Enter cage number: ")
    profileDirectory = input("Enter profile save directory: ")
    mouseName = mouseName
    mouseNumber = mouseName[len(mouseName) - 1]
    difficulty = "0"
    paw = "LEFT"
    sessionNumber = "0"

    os.mkdir("../../AnimalProfiles/" + str(mouseName))
    os.mkdir("../../AnimalProfiles/" + str(mouseName) + "/Analyses")
    os.mkdir("../../AnimalProfiles/" + str(mouseName) + "/Logs")
    os.mkdir("../../AnimalProfiles/" + str(mouseName) + "/Videos")
    os.mkdir("../../AnimalProfiles/" + str(mouseName) + "/Temp")

    saveFile = open("../../AnimalProfiles/" + str(mouseName) + "/" + str(mouseName) + "_save.txt", "w+")
    saveFile.write(str(RFID) + "\n")
    saveFile.write(str(mouseName) + "\n")
    saveFile.write(str(mouseNumber) + "\n")
    saveFile.write(str(cageNumber) + "\n")
    saveFile.write(str(difficulty) + "\n")
    saveFile.write(str(paw) + "\n")
    saveFile.write(str(sessionNumber) + "\n")
    saveFile.write(str(profileDirectory) + "\n")
    logFile = open("../../AnimalProfiles/" + str(mouseName) + "/Logs/" + str(mouseName) + "_session_history.csv", "w+")
    print("Profile created for " + str(mouseName) + "!")


for i in range(1,7):
    gen_profile("MOUSE" + str(i))


