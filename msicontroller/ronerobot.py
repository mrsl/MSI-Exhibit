import sys
import time
import glob
import atexit
import threading

from serial import Serial

class RoneRobot:
	"""Class for maintaining a connection to a r-one robot and writing data
	over serial to the robot.
	"""
	connection = None	# Serial connection to robot
	active = False		# Is the thread active?
	thread = None		# Thread object for monitoring robot
	line = ""

	def __init__(self):
		"""Constructor. Doesn't do much.
		"""
		atexit.register(self.stop)


	def start(self):
		"""Begins monitor thread.
		"""
		self.active = True

		self.thread = threading.Thread(
			target = self._monitor,
			name = "r-one Robot"
		)

		self.thread.daemon = True

		self.thread.start()


	def stop(self):
		"""Stops the active monitor thread. Disconnects from robot.
		"""
		self.active = False
		self.disconnectFromRobot()

		if self.thread:
			if self.thread.isAlive():
				self.thread.join()

			self.thread = None


	def writeline(self, line):
		"""Writes a line delimited by a '\n' to the connected robot.
		If there isn't a '\n' on the end of the line, appends one.
		Immediately returns if there is no robot connected.
		"""
		if not self.connection:
			return

		if line[-1] != '\n':
			line += '\n'

		try:
			self.connection.write(line)

		except:
			# self.disconnectFromRobot()
			pass


	def connectToRobot(self):
		"""Find and connect to a robot. Blocks until robot has been
		connected.
		"""
		candidates = glob.glob("/dev/ttyUSB*")

		if candidates:
			self.connection = Serial(
				candidates[0],
				baudrate = 230400,
				timeout = 1
			)

			print "Host robot connected!"


	def disconnectFromRobot(self):
		"""Disconnects from an active connection to a robot.
		"""
		if self.connection:
			print "Host robot disconnected!"

			self.connection.close()
			self.connection = None


	def processLine(self, line):
		"""Processes input from the robot. Does some action. Maybe.
		"""
		self.line += line

		if '\n' in line:
			ss = self.line.split('\n')

			print ss[0]

			self.line = '\n'.join(ss[1:])

	def _monitor(self):
		"""Maintain connection with a robot. Stays robust to unplugging
		and hotswapping of robots. Also reads data from robot.
		"""
		while self.active:
			if not self.connection:
				self.connectToRobot()
				time.sleep(1)
				continue

			try:
				data = self.connection.read(1)

				# print data

				if data:
					self.processLine(data)

			except:
				self.disconnectFromRobot()

			# time.sleep(0.3)


if __name__ == "__main__":
	hostRobot = RoneRobot()
	hostRobot.start()

	try:
		while True:
			pass

	except KeyboardInterrupt:
		hostRobot.stop()
		sys.exit()

