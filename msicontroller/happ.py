import sys
import time
import atexit
import threading

import usb.core
import usb.util

class HappDevice:
	"""Class for handling continuous input from a Happ Fighting UGCI.
	Upon error from reading, will call a full exit from the program.

	A call to start() will begin a monitor thread that processes all input
	from the device, calling registered functions on the rising or falling
	edge of an input.
	"""
	VENDOR_ID = 0x078b	# USB vendor ID.
	PRODUCT_ID = 0x0030	# USB product ID.

	reattach = False	# Have we detached from the kernel?
	endpoint = None		# USB endpoint to read from.

	active = False

	onKeys = {}		# Current status of all keys.
	keyOnFunctions = {}	# Function to trigger on a key's rising edge.
	keyOffFunctions = {}	# Function to trigger on a key's falling edge.

	device = None		# USB Device
	thread = None		# Monitor thread.
 
	def __init__(self):
		"""Constructor. Registers exit method.
		"""
		atexit.register(self.destroyDevice)


	def setupDevice(self):
		"""Finds and establishes a connection to the device. Or at
		least tries to.
		"""
		# Find device.
		self.device = usb.core.find(
			idVendor = self.VENDOR_ID,
			idProduct = self.PRODUCT_ID
		)

		if self.device:
			# Detach device from kernel and configure the device.
			print "Happ device connected!"
			
			self._detachDevice()
			self._setConfiguration()
			self._claimDevice()


	def destroyDevice(self):
		"""Cleanup. Release hold from device and reattach to kernel.
		"""
		self.stop()

		if self.device:
			self._releaseDevice()
			self._attachDevice()
			self._resetDevice()

			self.clearDeviceData()


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
		"""Stops monitor thread.
		"""
		self.active = False

		if self.thread:
			if self.thread.isAlive():
				self.thread.join()

			self.thread = None


	def _detachDevice(self):
		"""Detaches the device from the kernel.
		"""
		try:
			if self.device.is_kernel_driver_active(0):
				self.device.detach_kernel_driver(0)
				self.device.detach_kernel_driver(1)

				self.reattach = True

		except usb.core.USBError as e:
			raise IOError("Can't detach driver: %s" % str(e))

	
	def _attachDevice(self):
		"""Attaches the device to the kernel. Only works if the device
		was previously detached.
		"""
		if not self.reattach:
			return
		
		self.reattach = False

		try:
			if self.device.is_kernel_driver_active(0):
				self.device.attach_kernel_driver(0)
				self.device.attach_kernel_driver(1)

		except usb.core.USBError as e:
			raise IOError("Can't attach driver: %s" % str(e))

	
	def _claimDevice(self):
		"""Claims the device.
		"""
		usb.util.claim_interface(self.device, 0)
		usb.util.claim_interface(self.device, 1)


	def _releaseDevice(self):
		"""Releases claim on the device and cleans up resources.
		"""
		try:
			usb.util.release_interface(self.device, 0)
			usb.util.release_interface(self.device, 1)

		except usb.core.USBError as e:
			raise IOError("Can't release device: %s", str(e))
		
		usb.util.dispose_resources(self.device)


	def _resetDevice(self):
		"""Resets the device.
		"""
		try:	
			self.device.reset()

		except usb.core.USBError as e:
			if "Entity" not in str(e):
				raise IOError("Reset error: %s" % str(e))


	def _setConfiguration(self):
		"""Sets configuration of the device and grabs the endpoint we
		will be reading from.
		"""
		try:
			self.device.set_configuration()

		except usb.core.USBError as e:
			raise IOError("Can't set configuration: %s" % str(e))

		endpoints = []
		for configuration in self.device:
			for interface in configuration:
				for endpoint in interface:
					endpoints.append(endpoint)

		if not endpoints:
			raise IOError("No endpoints.")

		if len(endpoints) != 2:
			raise IOError("Incorrect number of endpoints.")

		self.endpoint = endpoints[0]


	def readData(self, timeout = 0):
		"""Reads data from the device under specified timeout
		constraint. A timeout of 0 will block until data is available.
		Returns data read.
		"""
		data = []
		try:
			data = self.device.read(
				self.endpoint.bEndpointAddress,
				self.endpoint.wMaxPacketSize,
				timeout = timeout
			) 
		
		except usb.core.USBError as e:
			# Timeout error.
			if "timed" in str(e):
				return data

			raise IOError("Read error: %s" % str(e))
		
		return data


	def getKeyStatus(self, key):
		"""Returns the current status of a key. True for on, False for
		off.
		"""
		if key in self.onKeys:
			return self.onKeys[key]

		else:
			return False


	def registerOnFunction(self, inKey, function):
		"""Registers a function to be called on inKey's rising edge.
		"""
		self.keyOnFunctions[inKey] = function


	def registerOffFunction(self, offKey, function):
		"""Registers a function to be called on offKey's falling edge.
		"""
		self.keyOffFunctions[offKey] = function


	def inputProcess(self, inputs):
		"""Processes an input line from the device, calling functions
		upon a key's status change.
		"""
		# Check for rising edge of the inputs.
		for inKey in inputs:
			if inKey not in self.onKeys:
				self.onKeys[inKey] = False

			if not self.onKeys[inKey]:
				if inKey in self.keyOnFunctions:
					self.keyOnFunctions[inKey]()

		# Check for falling edge of other keys.
		for onKey in self.onKeys.keys():
			if onKey not in inputs and self.onKeys[onKey]:
				if onKey in self.keyOffFunctions:
					self.keyOffFunctions[onKey]()

			self.onKeys[onKey] = False
		
		# Flag all inputs as on.
		for inKey in inputs:
			self.onKeys[inKey] = True


	def clearDeviceData(self):
		"""On device failure / exit, clear associated data.
		"""
		self.onKeys = {}
		self.endpoint = None
		self.device = None

		print "Happ device disconnected!"

	def _monitor(self):
		"""Monitors the device for input and processes the input keys.
		Handles disconnection gracefully by attempting to reconnect.
		"""
		inputs = []

		while self.active:
			# If there is no device, try to set one up
			if not self.device:
				self.setupDevice()
				continue

			try:
				data = self.readData(1000)

			# Device was unplugged, attempt to get it back
			except IOError:
				self.clearDeviceData()

			if not data:
				continue

			if data[0] == 14:
				if data[3] == 0:
					self.inputProcess(inputs)
					inputs = []

				else:
					inputs.append(data[3])


