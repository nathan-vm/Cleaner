import RPi.GPIO as GPIO
import time
import read_RPM
import threading
import setup_robo
import sys
import multiprocessing
from Gyro_new import Gyro


#from mpu6050 import mpu6050

class Control_robo:

    def __init__(self, encoder_1, encoder_2, SAMPLE_TIME, motor_1, motor_2):

        self.encoder_1 = encoder_1 ## LEFT ENCODER
        self.encoder_2 = encoder_2 ## RIGHT ENCODER
        ### RPM DATA TO USE ON PID
        self.RPM_1 = 0
        self.RPM_2 = 0

        self.SAMPLE_TIME = SAMPLE_TIME
        self.motor_1 = motor_1  ##LEFT MOTOR
        self.motor_2 = motor_2  ##RIGHT MOTOR
        
        ## SETUP PWM
        self.p = GPIO.PWM(self.motor_1.enable, 1000)
        self.p2 = GPIO.PWM(self.motor_2.enable, 1000)
        self.p.start(25)
        self.p2.start(25)

        ## SETUP START DUTY VALUES
        self.duty_1_value = 15
        self.duty_2_value = 15

        #self.TARGET = 80 # USE ONLY WITH PID ENCODER CONTROL

        ## SETUP INITIAL TARGETS TO RPM
        self.TARGET_1 = 80 #USE WITH PID ENCODER + GYRO CONTROL (DONT CHANGE WITH TIME)
        self.TARGET_2 = 80 #USE WITH PID ENCODER + GYRO CONTROL (THIS CHANGES WITH TIME)

        ## SETUP INITIAL TARGET TO GYRO
        self.TARGET_ANGLE = 0 # USE WITH PID ENCODER + GYRO CONTROL
        self.angle_z = 0    #VARIABLE WITH GYRO READ DATA
        
        self.select = 'p'
        self.gyro = Gyro()
        self.gyro.calibration()
        self.focus = 0


     
    def background_2(self):

        def run_2(self):

            ## CREATE THREAD TO READ IMU DATA
            print("Starting Thread 1")
            thread_gyro = threading.Thread(target = gyro_read, args = (self,))
            thread_gyro.daemon = True
            thread_gyro.start()

            ## CREAT THREAD TO READ ENCODERS DATA
            print("Starting Thread 2")
            thread_RPM = threading.Thread(target = rpm_read, args = (self,))
            thread_RPM.daemon = True
            thread_RPM.start()

            ### CREATE THREAD TO PID CONTROL
            print("Starting Thread 3")
            thread_PID = threading.Thread(target = pid_angle, args =(self,))
            thread_PID.daemon = True
            thread_PID.start()


        def rpm_read(self):

            while True:
                self.RPM_1 = self.encoder_1.RPM()
                self.RPM_2 = self.encoder_2.RPM()
                #time.sleep(SAMPLE_TIME/100) ## define the refresh rate to read RPM




        def gyro_read(self):

            ## THE REFRESH RATE ALREADY IS ON GYRO CLASS (DONT CHANGE THE RATE)
            while True:
                angle_data = self.gyro.reading()
                self.angle_z = angle_data['z']
                '''
                angle_x = angle_data['x']
                angle_y = angle_data['y']
                print("ANGLE DATA Z: ",self.angle_z)
                print("ANGLE DATA x: ", angle_x)
                print("ANGLE DATA Y: ", angle_y)
                '''
                ##REFRESH Z AXIS GYRO DATA WITH GYRO READ FREQUENCY
                ## aumentar frequencia do gyro ja que agora estamos usando thread independente? TESTAR

            ## CRIAR UMA THREAD TAMBEM PARA O RPM_READ?? talvez seja interessante
            ## uma thread para o controle pid e focus, outra pro read rpm e outra pro read gyro
            ## isso causaria interferencia de frequencias ou melhoraria o desempenho??
            ## o read_rpm tem uma frequencia, o gyro outra e o PID pode ser otimizado deixando-as separadas?



        def pid_angle(self):

            #KI MELHORES VALORES ATE AGORA
            '''
            KP = 0.0032
            KD = 0.0008
            KI = 0.00002
            '''

            error_prev = 0
            sum_z = 0

            ## PID RPM DATA
            KPr = 0.05
            KDr = 0.03
            KIr = 0.0005

            e1_prev = 0
            e2_prev = 0
            e1_sum = 0
            e2_sum = 0

            while True:

                ## CALCULATE ERROR FOR ANGLE DATA
                ## USES GLOBAL ANGLE READ AT READ_THREAD 
                error_z = self.TARGET_ANGLE - self.angle_z ##ERROR NEGATIVO DOBRANDO PRA DIREITA
                diff_z = (error_z - error_prev)/0.02 ## CHANGE THIS VALUE OF TIME IF CHANGE SAMPLE RATE
                print("error: ", error_z)

                ## CALL FOCUS FUNCTION TO FIND THE WAY IF TOO LOST
                '''
                if error_z > 35 or error_z < -35:
                    focus(self)
                '''
                    ## when here this thread stops the pid control to work at focus, is this a problem??
                    ## quando sair daqui tem que voltar a condição de output de cada motor
                    ## com o duty que tava

                ## CALL DIRECTION FUNCTION WITH PID TO ANGLE CONTROL
                direction(self, error_z, diff_z, sum_z)

                self.TARGET_2 = max(min(250, self.TARGET_2), 50)                

                ## CALCULATE ERROR FOR RPM DATA
                if self.RPM_1 < 600:
                    RPM_1_error = self.TARGET_1 - self.RPM_1 ##WILL TRY TO BE ARROUND 100
                    e1_diff = (RPM_1_error - e1_prev) ## DERIVATIVE ERROR
                if self.RPM_2 < 600:
                    RPM_2_error = self.TARGET_2 - self.RPM_2 ##WILL TRY TO STABILIZE ANGLE
                    e2_diff = (RPM_2_error - e2_prev)

                ##DERIVATIVE ERROR FOR RPM
                #e1_diff = (RPM_1_error - e1_prev)
                #e2_diff = (RPM_2_error - e2_prev)

                if self.select in ('w', 's', 't', 'y', 'h','l','m'):
                    self.duty_1_value = self.duty_1_value + (RPM_1_error * KPr) + (e1_diff * KDr) + (e1_sum * KIr)
                    self.duty_2_value = self.duty_2_value + (RPM_2_error * KPr) + (e2_diff * KDr) + (e2_sum * KIr)
                if self.select == 'p':
                    self.duty_1_value = 10
                    self.duty_2_value = 10


                self.duty_1_value = max(min(100,self.duty_1_value), 0)
                self.duty_2_value = max(min(100,self.duty_2_value),0)


                print("RPM 1: ", self.RPM_1)
                print("RPM 2: ", self.RPM_2)
                print("\n")
                print("DUTY VALUE: ", self.duty_1_value)
                print("DUTY VALUE 2: ", self.duty_2_value)
                print("\n")
                print("SOMA: ", round(sum_z,3))
                print("DIFF: ", round(diff_z,3))
                print("\n")
                print("TARGET 2: ", self.TARGET_2)
                print("TARGET 1: ", self.TARGET_1)
                print("\n")
                print("ERRO ENCODER 1: ", RPM_1_error)
                print("ERRO ENCODER 2: ", RPM_2_error)
                print("#####################")


                ## CHANGE DUTY CYCLE VALUES
                self.p.ChangeDutyCycle(self.duty_1_value)
                self.p2.ChangeDutyCycle(self.duty_2_value)


                time.sleep(self.SAMPLE_TIME) ## refresh rate to PID control 
                ## changing this rate may change the values of de constantes KP, KI, KD

                if self.select != 'p':
                    error_prev = error_z
                    sum_z += error_z

                ## ENCODERS NEW ERRORS DATA
                    e1_prev = RPM_1_error
                    e2_prev = RPM_2_error

                    e1_sum += RPM_1_error
                    e2_sum += RPM_2_error

        def direction(self, error_z, diff_z, sum_z):

            ## PID ANGLE DATA
            KP = 0.0032
            KD = 0.0008
            KI = 0.00002


            #### REFAZER OS TESTES DE DIREÇÃO NO BACKWARD PORQUE EU PERDI O ARQUIVO QUE TAVA CERTO 
            if self.select == 'w':
                if error_z > 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_1 - (error_z * KP) - (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("codiçao 1")
                elif error_z > 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_2 - (error_z * KP) - (diff_z * KD) - (sum_z * KI)
                    print("condicao 2")
                elif error_z < 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_1 - (error_z * KP) - (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("condicao 3")
                elif error_z < 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_2 - (error_z * KP) - (diff_z * KD) - (sum_z * KI)
                    print("condicao 4")

            if self.select == 's':
                if error_z > 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_1 + (error_z * KP) + (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("codiçao 1")
                elif error_z > 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_2 + (error_z * KP) + (diff_z * KD) + (sum_z * KI)
                    print("condicao 2")
                elif error_z < 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_1 + (error_z * KP) + (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("condicao 3")
                elif error_z < 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_2 + (error_z * KP) + (diff_z * KD) + (sum_z * KI)
                    print("condicao 4")





        def focus(self):


        
            ########### STOP ALL MOTORS ##########
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.LOW)

            ## CHANGE DUTY OF BOTH MOTORS TO MOTOR 1 DUTY (duty to 80rpm +-)
            self.p.ChangeDutyCycle(self.duty_1_value)
            self.p2.ChangeDutyCycle(self.duty_1_value)

            ## READ GYRO DATA AND TURN A LITTLE BIT TO THE RIGHT 
            ## PROCURA FICAR ENTRE O TARGET_ANGLE -10 E TARGET_ANGLE + 10 (20 graus de range)

            while self.angle_z < self.TARGET_ANGLE-10 or self.angle_z >self.TARGET_ANGLE+10:
                ## LEFT MOTOR FORWARD
                GPIO.output(self.motor_1.in1, GPIO.HIGH)
                GPIO.output(self.motor_1.in2, GPIO.LOW)
                ## RIGHT MOTOR BACKWARD
                GPIO.output(self.motor_1.in1, GPIO.LOW)
                GPIO.output(self.motor_1.in2, GPIO.HIGH)
                time.sleep(1.5) ## sleep 1.5 seconds

            ## STOP ALL MOTORS AGAIN
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            time.sleep(1.5) ## sleep for 1.5 seconds again

            ## criar condição pra retomar os motores com HIGH e LOW da ultima seleçao de direção
            ## VER COMO FAZER AS CONDIÇÕES SEM TER QUE FAZER MIL IFS IGUAIS AOS LA DE BAIXO
            ## se tiver que usar os ifs é só copiar os ifs da thread principal de direçao

                


        run_2(self)


    def set_speed(self, x):

        temp1 = 1
        self.select = x
        if x == 'r':
            print("run")
            if (temp1 == 1):
                ##LEFT MOTOR
                GPIO.output(self.motor_1.in1, GPIO.HIGH)
                GPIO.output(self.motor_1.in2, GPIO.LOW)
                ##RIGHT MOTOR
                GPIO.output(self.motor_2.in1, GPIO.HIGH)
                GPIO.output(self.motor_2.in2, GPIO.LOW)
                print("forward")

                x = 'z'
            else:
                ##LEFT MOTOR
                GPIO.output(self.motor_1.in1, GPIO.LOW)
                GPIO.output(self.motor_1.in2, GPIO.HIGH)
                ##RIGHT MOTOR
                GPIO.output(self.motor_2.in1, GPIO.LOW)
                GPIO.output(self.motor_2.in2, GPIO.HIGH)
                print("backward")
                temp1 = 0 
                x = 'z'


        elif x == 'p':
            print("stop")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            self.duty_1_value = 10
            self.duty_2_value = 10
            self.select = 'p'
            x='z'

        elif x == 'w':
            #print("forward")
            #self.gyro.calibration()
            self.duty_1_value = self.duty_1_value 
            self.duty_2_value = self.duty_2_value 
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.HIGH)
            GPIO.output(self.motor_2.in2, GPIO.LOW)

            temp1 = 1
            x = 'z'
            self.select = 'w'

        elif x == 's':
            print("backward")
            
            #self.gyro.calibration()
            self.duty_1_value = self.duty_1_value
            self.duty_2_value = self.duty_2_value 
          
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.HIGH)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.HIGH)
            temp1 = 0
            x = 's'
            self.select = 's'
            
        elif x == 'd':
            print("turn right")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            x='z'
            
        elif x == 'a':
            print("turn left")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.HIGH)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            x='z'
        
        elif x == 'y':
            print("axis rotation right")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.HIGH)
        
        elif x == 't':
            print("axis rotation left")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.HIGH)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.HIGH)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
        
        elif x == 'l':
            print("low")
            #self.p.ChangeDutyCycle(25)
            #self.p2.ChangeDutyCycle(25)
            self.TARGET_1 = 80
            self.TARGET_2 = 80
            x = 'z'

        elif x == 'm':
            print("medium")
            #self.p.ChangeDutyCycle(50)
            #self.p2.ChangeDutyCycle(50)
            self.TARGET_1 = 200
            self.TARGET_2 = 200
            x = 'z'

        elif x == 'h':
            print("high")
            #self.p.ChangeDutyCycle(100)
            #self.p2.ChangeDutyCycle(100)
            self.TARGET_1 = 250
            self.TARGET_2 = 250
            x = 'z'
        else:
            print("<<<  wrong data  >>>")