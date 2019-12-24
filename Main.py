import RPi.GPIO as GPIO
import time
import read_RPM
from setup_robo import *
from control_robo import *
import pigpio
import threading
import sys

##PINS

temp1 = 1


####################

##SETUP RPM MEASURING
RPM_GPIO = 4
RPM_GPIO_2 = 17
RUN_TIME = 60.0
SAMPLE_TIME = 2.0

pi = pigpio.pi()
pi2 = pigpio.pi()

###################

##SETUP ENCODERS

encoder_1 = read_RPM.reader(pi, RPM_GPIO)
encoder_2 = read_RPM.reader(pi2, RPM_GPIO_2)

###################

### SETUP MOTORS BCM PINS (EN, IN1, IN2) ###

motor_1 = Setup_robo(25,24,23)
motor_1.set_motors()


#### SET MOTOR 2 ###
motor_2 = Setup_robo(6,16,26)
motor_2.set_motors()

controle = Control_robo(encoder_1, encoder_2, SAMPLE_TIME, motor_1, motor_2)

###############################################################

print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run p-stop w-forward s-backward a-turn lef d-turn right g-axis rotation l-low m-medium h-high e-exit")
print("\n")


#controle.background() ## call PID encoder control only

controle.background_2() ## call PID encoder + gyro control

start = time.time()
while (1):
    
    x = input()
    if x != 'e':
        controle.set_speed(x)

    elif x == 'e':
        GPIO.cleanup()
        print("GPIO Clean up")
        print("Thread end")
        sys.exit()
        break

print("Please enter the defined data to continue.....")
