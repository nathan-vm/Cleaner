from mpu6050 import mpu6050
import time
import math


class Gyro:

	def __init__(self):
	
		self.gyro = mpu6050(0x68)
		self.gyro.set_gyro_range(0x08)
		self.gyro.set_accel_range(0x10)

		## gyro instant data
		self.gyro_full_data = 0
		self.gyro_x = 0
		self.gyro_y = 0
		self.gyro_z = 0
		## gyro calibration data
		self.gyro_x_cal = 0
		self.gyro_y_cal = 0
		self.gyro_z_cal = 0

		##gyro angle data
		self.angle_pitch_x = 0
		self.angle_roll_y = 0
		self.angle_rotate_z = 0

		##accel angle data
		self.angle_pitch_acc = 0
		self.angle_roll_acc = 0


		## ACC INSTANT DATA
		self.accel_full_data = 0
		self.acc_x = 0
		self.acc_y = 0
		self.acc_z = 0

		## CONTROL
		self.set_gyro_angles = False

		##OUTPUTS
		self.angle_pitch_output = 0
		self.angle_roll_output = 0

		self.SAMPLE_RATE = 0.02 #seconds = 50Hz


	def calibration(self):
		print("Calibrando")
		self.gyro_x = 0
		self.gyro_y = 0
		self.gyro_z = 0
		self.gyro_x_cal = 0
		self.gyro_y_cal = 0
		self.gyro_z_cal = 0
		for i in range(50):
			self.read_mpu_data()
			self.gyro_x_cal+= self.gyro_x
			self.gyro_y_cal+= self.gyro_y
			self.gyro_z_cal+= self.gyro_z
			time.sleep(0.003)
		print("Calibration datas: ")	
		self.gyro_x_cal /= 50
		self.gyro_y_cal /= 50
		self.gyro_z_cal /= 50

		print("\nx: %.2f" %self.gyro_x_cal)
		print("\ny: %.2f" %self.gyro_y_cal)
		print("\nz: %.2f" %self.gyro_z_cal)


	def reading(self):

		self.read_mpu_data()

		self.gyro_x -= self.gyro_x_cal
		self.gyro_y -= self.gyro_y_cal
		self.gyro_z -= self.gyro_z_cal

		self.angle_pitch_x += self.gyro_x * 0.036#0.0144
		self.angle_roll_y += self.gyro_y * 0.036#0.0144
		self.angle_rotate_z += self.gyro_z * 0.036#0.0144


		#### X CONDITION ###
		if self.angle_pitch_x>=360:
			x = self.angle_pitch_x - 360
			self.angle_pich_x = x
		elif self.angle_pitch_x <= -360:
			x = self.angle_pitch_x + 360
			self.angle_pitch_x = x
		else:
			x = self.angle_pitch_x

		#### Y CONDITION ###
		if self.angle_roll_y >= 360:
			y = self.angle_roll_y - 360
			self.angle_roll_y = y
		elif self.angle_roll_y <= -360:
			y = self.angle_roll_y + 360
			self.angle_roll_y = y
		else:
			y = self.angle_roll_y

		### Z CONDITION ###
		if self.angle_rotate_z >= 360:
			z = self.angle_rotate_z - 360
			self.angle_rotate_z = z
		elif self.angle_rotate_z <= -360:
			z = self.angle_rotate_z + 360
			self.angle_rotate_z = z
		else:
			z = self.angle_rotate_z

		x = round(x,3)
		y = round(y,3)
		z = round(z,3)

		time.sleep(self.SAMPLE_RATE)
		return {'x': x, 'y': y, 'z': z}

		#print("\nx: %.2f" %self.angle_pitch_x)
		#print("\ny: %.2f" %self.angle_roll_y)
		#print("\nz: %.2f" %self.angle_rotate_z)
		

## FUNÇAO PRA TESTE APENAS, DESCOMENTAR O FINAL DO CODIGO PRA TESTAR
	def reading_while(self):

		while True:
			self.read_mpu_data()

			self.gyro_x -= self.gyro_x_cal
			self.gyro_y -= self.gyro_y_cal
			self.gyro_z -= self.gyro_z_cal

			self.angle_pitch_x += self.gyro_x * 0.036#0.0144
			self.angle_roll_y += self.gyro_y * 0.036#0.0144
			self.angle_rotate_z += self.gyro_z * 0.036#0.0144



			#### X CONDITION ###
			if self.angle_pitch_x>=360:
				x = self.angle_pitch_x - 360
				self.angle_pich_x = x
			elif self.angle_pitch_x <= -360:
				x = self.angle_pitch_x + 360
				self.angle_pitch_x = x
			else:
				x = self.angle_pitch_x

			#### Y CONDITION ###
			if self.angle_roll_y >= 360:
				y = self.angle_roll_y - 360
				self.angle_roll_y = y
			elif self.angle_roll_y <= -360:
				y = self.angle_roll_y + 360
				self.angle_roll_y = y
			else:
				y = self.angle_roll_y

			### Z CONDITION ###
			if self.angle_rotate_z >= 360:
				z = self.angle_rotate_z - 360
				self.angle_rotate_z = z
			elif self.angle_rotate_z <= -360:
				z = self.angle_rotate_z + 360
				self.angle_rotate_z = z
			else:
				z = self.angle_rotate_z


			#return self.angle_rotate_z
			print("\nx: %.2f" %x)
			print("\ny: %.2f" %y)
			print("\nz: %.2f" %z)
			time.sleep(self.SAMPLE_RATE)		



	def read_mpu_data(self):

		## GET GYRO DATA (ALREADY IN SCALE 4G /65.5)
		self.gyro_full_data = self.gyro.get_gyro_data()
		self.gyro_x = self.gyro_full_data['x']
		self.gyro_y = self.gyro_full_data['y']
		self.gyro_z = self.gyro_full_data['z']

		## GET ACCEL DATA
		self.accel_full_data = self.gyro.get_accel_data()
		self.acc_x = self.accel_full_data['x']
		self.acc_y = self.accel_full_data['y']
		self.acc_z = self.accel_full_data['z']


#giroscopio = Gyro()
#giroscopio.calibration()
#giroscopio.reading_while()

## > 60 or < -60