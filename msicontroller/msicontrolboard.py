import sys
import copy
import time
import threading

import happ
import ronerobot
import analogjoystick

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

class MSIControlBoard:
	happDevice = None		# Happ Control Board for input
	hostRobot = None		# Host robot to use for output
	joystick = None			# Analog joystick for other input
	line = "UI000000000000\n"	# Line to output to host robot

	active = False			# Is the monitor thread active
	monitorThread = None		# Monitoring thread
	outputThread = None		# Output thread

	status = {}			# Status of all keys

	def __init__(self):
		"""Initializes both devices to be used on the board, the Happ
		controller and the robot. Starts both of their monitor threads
		as well.
		"""
		self.happDevice = happ.HappDevice()
		self.happDevice.start()

		self.joystick = analogjoystick.AnalogJoystick()
		self.joystick.start()

		self.hostRobot = ronerobot.RoneRobot()
		self.hostRobot.start()

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
		oldStatus = copy.copy(self.status)

		self.status['e'] = self.happDevice.getKeyStatus(EAST_STICK)
		self.status['n'] = self.happDevice.getKeyStatus(NORTH_STICK)
		self.status['s'] = self.happDevice.getKeyStatus(SOUTH_STICK)
		self.status['w'] = self.happDevice.getKeyStatus(WEST_STICK)

		self.status['r'] = self.happDevice.getKeyStatus(RED_BUTTON)
		self.status['y'] = self.happDevice.getKeyStatus(YELLOW_BUTTON)
		self.status['g'] = self.happDevice.getKeyStatus(GREEN_BUTTON)
		self.status['b'] = self.happDevice.getKeyStatus(BLUE_BUTTON)

		diff = False

		for key in oldStatus.keys():
			if self.status[key] != oldStatus[key]:
				diff = True
				break

		return diff

	def updateStatusJoystick(self):
		oldStatus = copy.copy(self.status)

		self.status = copy.copy(self.joystick.status)

		diff = False

		for key in oldStatus.keys():
			if self.status[key] != oldStatus[key]:
				diff = True
				break

		return diff

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

			if self.happDevice.device:
				f = self.updateStatus()

			if self.joystick.device and not self.happDevice.device:
				f = self.updateStatusJoystick()	

			if f:
				self.line = self.getCommandLine()
				print "Output!", self.line

	def getStatus(self):
		return self.status

	def _output(self):
		while self.active:
			self.sendCommandLine(self.line)
			time.sleep(OUTPUT_INTERVAL)

if __name__ == "__main__":
	msiBoard = MSIControlBoard()
	msiBoard.start()

	# display = display.Display(msiBoard)
	# display.start()

	try:
		while True:
			pass

	except KeyboardInterrupt:
		msiBoard.stop()
		sys.exit(0)