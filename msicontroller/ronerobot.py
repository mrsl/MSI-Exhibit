import sys
import time
import glob
import atexit
import threading

from serial import Serial

IDLE = 0
CLUSTER_ACTIVE = 1
CLUSTER_LOADING = 2
FLOCK_ACTIVE = 3
FLOCK_LOADING = 4
FOLLOW_ACTIVE = 5
FOLLOW_LOADING = 6

MODE_IDLE = 0
MODE_FOLLOW = 1
MODE_FLOCK = 2
MODE_CLUSTER = 3

class RoneRobot:
	"""Class for maintaining a connection to a r-one robot and writing data
	over serial to the robot.
	"""
	connection = None	# Serial connection to robot
	active = False		# Is the thread active?
	thread = None		# Thread object for monitoring robot
	line = ""
        mode = IDLE

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

			l = ss[0]
                        if "MSIExhibit" in l:
                                try:
                                        tag, mode, building = l.split()
                                        junk, mode = mode.split("=")
                                        junk, building = building.split("=")

                                        mode = int(mode)
                                        building = int(building)

                                        if mode == MODE_IDLE:
                                                self.mode = IDLE

                                        if mode == MODE_FOLLOW:
                                                if building:
                                                        self.mode = FOLLOW_LOADING
                                                else:
                                                        self.mode = FOLLOW_ACTIVE

                                        if mode == MODE_FLOCK:
                                                if building:
                                                        self.mode = FLOCK_LOADING
                                                else:
                                                        self.mode = FLOCK_ACTIVE

                                        if mode == MODE_CLUSTER:
                                                if building:
                                                        self.mode = CLUSTER_LOADING
                                                else:
                                                        self.mode = CLUSTER_ACTIVE

                                except Exception as e:
                                        print e.strerror
                                        pass

			self.line = '\n'.join(ss[1:])

	def getMode(self):
		return self.mode

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

