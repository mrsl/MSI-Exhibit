import sys
import copy
import time
import threading

import happ
import happ2
import ronerobot
import analogjoystick
import display2

# Values of keys on the Happ device
EAST_STICK = 8
NORTH_STICK = 17
SOUTH_STICK = 22
WEST_STICK = 26

RED_BUTTON = 30
YELLOW_BUTTON = 31
GREEN_BUTTON = 32
BLUE_BUTTON = 33

# How fast to write data to the robot
OUTPUT_INTERVAL = 0.05

DZ = 0.01

class MSIControlBoard:
	happDevice = None		# Happ Control Board for input
	happDevice2 = None		# Happ Control Board for input
	hostRobot = None		# Host robot to use for output
	joystick = None			# Analog joystick for other input
	line = "UI000000000000\n"	# Line to output to host robot

	active = False			# Is the monitor thread active
	monitorThread = None		# Monitoring thread
	outputThread = None		# Output thread

	status = {}			# Status of all keys
	stick = { 'x' : 0, 'y' : 0 }

	loading = False
	mode = 0

	def __init__(self):
		"""Initializes both devices to be used on the board, the Happ
		controller and the robot. Starts both of their monitor threads
		as well.
		"""
		self.happDevice = happ.HappDevice()
		self.happDevice.start()

		self.happDevice2 = happ2.HappFlyDevice()
		self.happDevice2.start()

		self.joystick = analogjoystick.AnalogJoystick()
		self.joystick.start()

		self.hostRobot = ronerobot.RoneRobot()
		self.hostRobot.start()

		self.status['e'] = False
		self.status['n'] = False
		self.status['s'] = False
		self.status['w'] = False

		self.status['r'] = False
		self.status['y'] = False
		self.status['g'] = False
		self.status['b'] = False

	def start(self):
		"""Begins monitor thread and output thread.
		"""
		self.active = True

		self.monitorThread = threading.Thread(
			target = self._monitor,
			name = "MSI Board Monitor"
		)

		self.monitorThread.daemon = True
		self.monitorThread.start()

		self.outputThread = threading.Thread(
			target = self._output,
			name = "MSI Board Output"
		)

		self.outputThread.daemon = True
		self.outputThread.start()

	def stop(self):
		"""Stops the active monitor and output threads.
		"""
		self.active = False

		self.happDevice.stop()
		self.happDevice2.stop()
		self.hostRobot.stop()
		self.joystick.stop()

		if self.monitorThread:
			if self.monitorThread.isAlive():
				self.monitorThread.join()

			self.monitorThread = None

		if self.outputThread:
			if self.outputThread.isAlive():
				self.outputThread.join()

			self.outputThread = None

	def updateStatus(self):
		"""Updates status of all keys on the board. Returns True if
		there was a change, false if there was not.
		"""
		self.status['e'] = self.happDevice.getKeyStatus(EAST_STICK)
		self.status['n'] = self.happDevice.getKeyStatus(NORTH_STICK)
		self.status['s'] = self.happDevice.getKeyStatus(SOUTH_STICK)
		self.status['w'] = self.happDevice.getKeyStatus(WEST_STICK)

		self.status['r'] = self.happDevice.getKeyStatus(RED_BUTTON)
		self.status['y'] = self.happDevice.getKeyStatus(YELLOW_BUTTON)
		self.status['g'] = self.happDevice.getKeyStatus(GREEN_BUTTON)
		self.status['b'] = self.happDevice.getKeyStatus(BLUE_BUTTON)

	def updateStatusFly(self):
		self.status['r'] = self.happDevice2.getKeyStatus(2)
		self.status['b'] = self.happDevice2.getKeyStatus(3)
		self.status['g'] = self.happDevice2.getKeyStatus(4)
		self.status['y'] = self.happDevice2.getKeyStatus(5)

	def updateStatusJoystick(self):
		self.status['e'] = self.joystick.status['e']
		self.status['n'] = self.joystick.status['n']
		self.status['s'] = self.joystick.status['s']
		self.status['w'] = self.joystick.status['w']

		self.stick['x'] = self.joystick.stick['x']
		self.stick['y'] = self.joystick.stick['y']

	def getNewCommandLine(self):
		if not self.status:
			return "UI000000000000000000\n"

		xs = self.stick['x']
		ys = self.stick['y']
		

		if abs(xs) < DZ:
			xs = 0
		else:
			xs -= DZ

		if abs(ys) < DZ:
			ys = 0
		else:
			ys -= DZ

                x = int(xs * 128)
                y = -int(ys * 128)
		
                x += 128
		y += 128

		if x > 255:
			x = 255
		if y > 255:
			y = 255

		if x < 0:
			x = 0
		if y < 0:
			y = 0

                line = "UI"

		line += "%02X%02X" % (x, y)
		
		buttonValue = 0

		if self.status['b']:
			buttonValue += 1

		if self.status['g']:
			buttonValue += 2

		if self.status['y']:
			buttonValue += 4 
		
		if self.status['r']:
			buttonValue += 8 


		line += "%0.2x" % buttonValue

		return line + "000000000000\n"


	def getCommandLine(self):
		"""Finds the command line to send to the robot from the keys
		set on the board. Returns the new command line.
		"""
		if not self.status:
			return "UI000000000000\n"

		command = "UI0000"

		directionValue = 0

		if self.status['e']:
			directionValue += 1

		if self.status['w']:
			directionValue += 2

		if self.status['s']:
			directionValue += 4

		if self.status['n']:
			directionValue += 8

		command += "%0.2x" % directionValue

		buttonValue = 0

		if self.status['b']:
			buttonValue += 1

		if self.status['g']:
			buttonValue += 2

		if self.status['r']:
			buttonValue += 4

		if self.status['y']:
			buttonValue += 8

		command += "%0.2x" % buttonValue

		command += "0000\n"

		return command

	def sendCommandLine(self, line):
		"""Sends a command to the robot currently attached.
		"""
		self.hostRobot.writeline(line)
	
	def _monitor(self):
		while self.active:
			f = False

			oldstatus = self.status.copy()

			if self.happDevice.device:
				f = self.updateStatus()
                                self.line = self.getCommandLine()

			if self.happDevice2.device and \
			    not self.happDevice.device:
				f = self.updateStatusFly()

			if self.joystick.device and not self.happDevice.device:
				f = self.updateStatusJoystick()

			self.line = self.getNewCommandLine()
			

	def getStatus(self):
		return self.status

	def getMode(self):
		return 0

	def _output(self):
		while self.active:
			self.sendCommandLine(self.line)
			time.sleep(OUTPUT_INTERVAL)

			if self.happDevice2:
				self.happDevice2.clearInputs()


if __name__ == "__main__":
	msiBoard = MSIControlBoard()
	msiBoard.start()
	
	display = display2.Display(msiBoard)
	display.start()
