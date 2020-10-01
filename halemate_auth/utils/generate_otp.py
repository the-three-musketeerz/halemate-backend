import math
import random


def generateOTP():
    string = '0123456789'
    OTP = ""
    length = len(string)
    for i in range(6):
        OTP += string[math.floor(random.random() * length)]

    return OTP
