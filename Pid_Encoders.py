
    #PID CONTROL FOR RPM ONLY
    def background(self):

        def run(self):
            print("Starting Thread 1")
            thread1 = threading.Thread(target = pid_control, args = (self,))
            thread1.daemon = True
            thread1.start()


        def pid_control(self):

            ### PID TARGET AND COEFFICIENTS
            #TARGET = 100
            #KP = 0.02
            #KD = 0.01
            #KI = 0.0001


            ## PID RPM DATA
            KP = 0.05
            KD = 0.03
            KI = 0.0005

            e1_prev_error = 0
            e2_prev_error = 0


            e1_sum_error = 0
            e2_sum_error = 0
            
            while True:
        
                RPM = self.encoder_1.RPM()
                RPM_2 = self.encoder_2.RPM()
                print("MOTOR 1 ={}".format(int(RPM+0.5)))
                print("MOTOR 2 ={}".format(int(RPM_2+0.5)))

                if RPM < 600:
                    e1_error = self.TARGET - RPM
                if RPM_2 < 600:
                    e2_error = self.TARGET - RPM_2


                ## Diferencial error - better with delta "e" than with previous "e"?
                e1_diff = (e1_error - e1_prev_error)
                e2_diff = (e2_error - e2_prev_error)

                ## SET DUTY CYCLE VALUES FOR MOTORS
                if self.select in ('w', 's', 't', 'y', 'h','l','m'):
                    self.duty_1_value = self.duty_1_value + (e1_error * KP) + (e1_diff * KD) + (e1_sum_error * KI)
                    self.duty_2_value = self.duty_2_value + (e2_error * KP) + (e2_diff * KD) + (e1_sum_error * KI)
                elif self.select in ('d', 'h', 'l', 'm'):
                    self.duty_1_value = self.duty_1_value + (e1_error * KP) + (e1_prev_error * KD) + (e1_sum_error * KI)
                elif self.select in ('a', 'h','l','m'):
                    self.duty_2_value = self.duty_2_value + (e2_error * KP) + (e2_prev_error * KD) + (e2_sum_error * KI)


                ## DISCARD DUTY OVER 100 OR LESS THAN 0
                self.duty_1_value = max(min(100,self.duty_1_value), 0)
                self.duty_2_value = max(min(100, self.duty_2_value), 0)

                print("DUTY VALUE: ", self.duty_1_value)
                print("DUTY VALUE 2: ", self.duty_2_value)

                ## CHANGE DUTY CYCLE VALUES
                self.p.ChangeDutyCycle(self.duty_1_value)
                self.p2.ChangeDutyCycle(self.duty_2_value)

                
                time.sleep(self.SAMPLE_TIME/100) ## change the frequency 
                ## SET PREVIOUS ERROR
                e1_prev_error = e1_error
                e2_prev_error = e2_error

                ## INTEGRAL ERROR
                e1_sum_error += e1_error
                e2_sum_error += e2_error

                print("error: ", e1_error)
                print("error2: ", e2_error)
                print("error soma: ", e1_sum_error)
                print("erro soma 2: ", e2_sum_error)




        run(self)
 