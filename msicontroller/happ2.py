import struct
import time
import sys
import re
import threading

INPUT_KEY = "80000000000000 e0b0ffdf01cfffff fffffffffffffffe"

def find_buttons():
        dev_file = open("/proc/bus/input/devices", "r")

        dev = ""
        for line in dev_file.readlines():
                dev += line

                if line == "\n":
                        if INPUT_KEY in dev:
                                m = re.findall("event\d+", dev)
                                return m[0]
                        dev = ""

        return None

def read_event(in_file):
        #long int, long int, unsigned short, unsigned short, unsigned int
        FORMAT = 'llHHI'
        EVENT_SIZE = struct.calcsize(FORMAT)
        event = in_file.read(EVENT_SIZE)

        if event:
                (tv_sec, tv_usec, type, code, value) = \
                    struct.unpack(FORMAT, event)

                return (type, code, value, tv_sec, tv_usec)

        else:
                return None

class HappFlyDevice:
        active = False
        thread = None # Monitor thread.
        device = None
	onKeys = {}   # Current status of all keys.

        def start(self):
		"""Start monitor thread.
		"""
		self.active = True

		self.thread = threading.Thread(
			target = self._monitor,
			name = "Happ Device"
		)

		self.thread.daemon = True

		self.thread.start()

        def stop(self):
                self.device.close()

                self.active = False

		if self.thread:
			if self.thread.isAlive():
				self.thread.join()

			self.thread = None

        def setupDevice(self):
                ev = find_buttons()

                infile_path = "/dev/input/" + ev
                self.device = open(infile_path, "rb")

        def clearDeviceData(self):
                self.device = None

        def inputProcess(self, inputs):
		for key in self.onKeys.keys():
			self.onKeys[key] = False

                self.onKeys[inputs[0]] = True

                print self.onKeys

	def getKeyStatus(self, key):
		if key in self.onKeys:
			return self.onKeys[key]

		else:
			return False

        def readData(self):
                event = read_event(self.device)

                if event == None:
                        raise IOError

                return event

        def _monitor(self):
		inputs = []

		while self.active:
			# If there is no device, try to set one up
			if not self.device:
				self.setupDevice()
				continue

			try:
				data = self.readData()

			# Device was unplugged, attempt to get it back
			except IOError:
				self.clearDeviceData()

			if not data:
				continue

			if data[0] == 1:
				if data[2] == 0:
					self.inputProcess(inputs)
					inputs = []

				else:
					inputs.append(data[1])



# infile_path = "/dev/input/" + ev
# in_file = open(infile_path, "rb")
#
# while 1:
#         event = read_event(in_file)
#
#         if not event:
#                 break
#
#         type, code, value, tv_sec, tv_usec = event
#         print type, code, value
#
# in_file.close()


