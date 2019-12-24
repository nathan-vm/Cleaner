import RPi.GPIO as GPIO
import gpiozero
import time
import control_robo

class Setup_robo:

    def __init__(self, enable, in1, in2):

        self.enable = enable
        self.in1 = in1
        self.in2 = in2
        #self.p = GPIO.PWM(enable, 1000)

    def set_motors(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.enable, GPIO.OUT)
        ##SET ALL LOW TO START###
        GPIO.output(self.in1, 0)
        GPIO.output(self.in2, 0)