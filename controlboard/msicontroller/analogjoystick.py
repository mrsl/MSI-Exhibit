import threading
import glob

class AnalogJoystick:
	status = {}

	active = False

	device = None		# USB Device
	thread = None		# Monitor thread.

	def __init__(self):
		for c in 'nesw':
			self.status[c] = False

	def start(self):
		self.active = True

		self.thread = threading.Thread(
			target = self._monitor,
			name = "Analog Joystick Device"
		)

		self.thread.daemon = True

		self.thread.start()


	def stop(self):
		self.stop()

		if self.device:
			self.device.close()

	def attemptConnect(self):
		try:
			devices = glob.glob("/dev/input/js*")

			for device in devices:
				self.device = open(device, 'r')

		except IOError:
			pass

	def processMessage(self, msg):
		num = int(msg[5], 16)

		percent254 = (float(num) - 128.0) / 126.0
		percent128 = float(num) / 127.0

		if msg[6] == '01': # Button
			if msg[4] == '01':
				self.status[msg[7]] = True
			else:
				self.status[msg[7]] = False

		elif msg[7] == '04': # D-pad left/right
			if msg[4] == 'FF':
				self.status['w'] = True
			elif msg[4] == '01':
				self.status['e'] = True
			else:
				self.status['w'] = False
				self.status['e'] = False

		elif msg[7] == '05': # D-pad up/down
			if msg[4] == 'FF':
				self.status['s'] = True
			elif msg[4] == '01':
				self.status['n'] = True
			else:
				self.status['n'] = False
				self.status['s'] = False

		elif msg[7] == '00': # Left Joystick left/right
			if num >= 128:
				self.status['llr'] = -1 + percent254
			elif num <= 127 and num != 0:
				self.status['llr'] = percent128
			else:
				self.status['lr'] = 0

		elif msg[7] == '01': # Left Joystick up/down
			if num >= 128:
				self.status['lud'] = 1 - percent254
			elif num <= 127 and num != 0:
				self.status['lud'] = -percent128
			else:
				self.status['lud'] = 0

		elif msg[7] == '02': # Right Joystick left/right
			if num >= 128:
				self.status['rlr'] = -1 + percent254
			elif num <= 127 and num != 0:
				self.status['rlr'] = percent128
			else:
				self.status['rlr'] = 0

		elif msg[7] == '03': # Right Joystick up/ down
			if num >= 128:
				self.status['rud'] = 1 - percent254
			elif num <= 127 and num != 0:
				self.status['rud'] = -percent128
			else:
				self.status['rud'] = 0

		if 'rud' in self.status:
			if not self.status['n'] and not self.status['s']:
				if self.status['rud'] > .5:
					self.status['s'] = False
					self.status['n'] = True

				elif self.status['rud'] < -.5:
					self.status['n'] = False
					self.status['s'] = True

				else:
					self.status['n'] = False
					self.status['s'] = False

		if 'rlr' in self.status:
			if not self.status['e'] and not self.status['w']:
				if self.status['rlr'] > .5:
					self.status['w'] = False
					self.status['e'] = True

				elif self.status['rlr'] < -.5:
					self.status['e'] = False
					self.status['w'] = True

				else:
					self.status['e'] = False
					self.status['w'] = False

		print self.status

	def _monitor(self):
		msg = []

		while self.active:
			if not self.device:
				self.attemptConnect()
				continue

			try:
				for char in self.device.read(1):
					msg += ['%02X' % ord(char)]

					if len(msg) == 8:
						self.processMessage(msg)

						msg = []
			except IOError:
				self.device.close()
				self.device = None

if __name__ == "__main__":
	j = AnalogJoystick()
	j.start()

	while True:
		pass