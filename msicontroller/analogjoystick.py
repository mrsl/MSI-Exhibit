import threading
import glob

DM = 0.4

class AnalogJoystick:
	status = {}
	stick = { 'x' : 0, 'y' : 0 }
	maxs = { 'x' : DM, 'y' : DM }
	mins = { 'x' : -DM, 'y' : -DM }
	cens = { 'x' : 0, 'y' : 0 }

	active = False

	device = None		# USB Device
	thread = None		# Monitor thread.


	x = 0
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
		if self.device:
			self.device.close()

	def attemptConnect(self):
		try:
			devices = glob.glob("/dev/input/js*")

			for device in devices:
				self.device = open(device, 'r')
				print "Joystick connected!"

		except IOError:
			pass

	def processMessage(self, msg):
		num = int(msg[5], 16)

		percent254 = (float(num) - 128.0) / 126.0
		percent128 = float(num) / 127.0

		readStat = {}

		if msg[6] == '01': # Button
			if msg[4] == '01':
				readStat[msg[7]] = True
			else:
				readStat[msg[7]] = False

		elif msg[7] == '04': # D-pad left/right
			if msg[4] == 'FF':
				readStat['dw'] = True
			elif msg[4] == '01':
				readStat['de'] = True
			else:
				readStat['dw'] = False
				readStat['de'] = False

		elif msg[7] == '05': # D-pad up/down
			if msg[4] == 'FF':
				readStat['ds'] = True
			elif msg[4] == '01':
				readStat['dn'] = True
			else:
				readStat['dn'] = False
				readStat['ds'] = False

		elif msg[7] == '00': # Left Joystick left/right
			if num >= 128:
				readStat['llr'] = -1 + percent254
			elif num <= 127 and num != 0:
				readStat['llr'] = percent128
			else:
				readStat['lr'] = 0

		elif msg[7] == '01': # Left Joystick up/down
			if num >= 128:
				readStat['lud'] = 1 - percent254
			elif num <= 127 and num != 0:
				readStat['lud'] = -percent128
			else:
				readStat['lud'] = 0

		elif msg[7] == '02': # Right Joystick left/right
			if num >= 128:
				readStat['rlr'] = -1 + percent254
			elif num <= 127 and num != 0:
				readStat['rlr'] = percent128
			else:
				readStat['rlr'] = 0

		elif msg[7] == '03': # Right Joystick up/ down
			if num >= 128:
				readStat['rud'] = 1 - percent254
			elif num <= 127 and num != 0:
				readStat['rud'] = -percent128
			else:
				readStat['rud'] = 0

		if 'lud' in readStat:
			self.stick['y'] = readStat['lud']
			
			if self.stick['y'] > self.maxs['y']:
				self.maxs['y'] = self.stick['y']

			if self.stick['y'] < self.mins['y']:
				self.mins['y'] = self.stick['y']

			if self.stick['y'] > self.cens['y']:
				self.stick['y'] = self.stick['y'] / self.maxs['y']

				if self.stick['y'] > 1.0:
					self.stick['y'] = 1.0;
			
			if self.stick['y'] < self.cens['y']:
				self.stick['y'] = -self.stick['y'] / self.mins['y']

				if self.stick['y'] < -1.0:
					self.stick['y'] = -1.0;

		if 'llr' in readStat:
			self.stick['x'] = readStat['llr']
			
			if self.stick['x'] > self.maxs['x']:
				self.maxs['x'] = self.stick['x']

			if self.stick['x'] < self.mins['x']:
				self.mins['x'] = self.stick['x']
			
			if self.stick['x'] > self.cens['x']:
				self.stick['x'] = self.stick['x'] / self.maxs['x']

				if self.stick['x'] > 1.0:
					self.stick['x'] = 1.0;
			
			if self.stick['x'] < self.cens['x']:
				self.stick['x'] = -self.stick['x'] / self.mins['x']

				if self.stick['x'] < -1.0:
					self.stick['x'] = -1.0;

		
		if not self.x % 10:	
			print self.stick, self.maxs, self.mins

		self.x += 1

		if 'lud' in readStat:
			if readStat['lud'] > .5:
				self.status['s'] = False
				self.status['n'] = True

			elif readStat['lud'] < -.5:
				self.status['n'] = False
				self.status['s'] = True

			else:
				self.status['n'] = False
				self.status['s'] = False
		else:
			self.status['n'] = False
			self.status['s'] = False

		if 'llr' in readStat:
			if readStat['llr'] > .5:
				self.status['w'] = False
				self.status['e'] = True

			elif readStat['llr'] < -.5:
				self.status['e'] = False
				self.status['w'] = True

			else:
				self.status['e'] = False
				self.status['w'] = False
		else:
			self.status['e'] = False
			self.status['w'] = False

		if '00' in readStat:
			self.status['r'] = readStat['00']
		else:
			self.status['r'] = False

		if '01' in readStat:
			self.status['g'] = readStat['01']
		else:
			self.status['g'] = False

		if '02' in readStat:
			self.status['b'] = readStat['02']
		else:
			self.status['b'] = False

		if '03' in readStat:
			self.status['y'] = readStat['03']
		else:
			self.status['y'] = False


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
