import os
import math
import pygame
from pygame.locals import *

FPS = 60

riceImgPath = "../../resources/rice.png"
mrslImgPath = "../../resources/mrsl.png"

class Colors:
	OFFWHITE = (240, 240, 240)
	OFFBLACK = (20, 20, 20)
	OFFGREY = (60, 60, 60)
	RED = (240, 30, 30)
	OFFRED = (150, 60, 60)
	BLUE = (20, 20, 240)
	OFFBLUE = (60, 60, 150)
	GREEN = (30, 240, 30)
	OFFGREEN = (60, 150, 60)
	YELLOW = (240, 240, 30)
	OFFYELLOW = (150, 150, 60)

class Display:
	SIZE = (640, 480)

	mode = 0
	oscillator = 0
	tick = 0

	def __init__(self, fb = False):

		if fb:
			driver = 'directfb'
			if not os.getenv('SDL_VIDEODRIVER'):
				os.putenv('SDL_VIDEODRIVER', driver)

		pygame.display.init()
		pygame.font.init()

		self.clock = pygame.time.Clock()

		self.SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
		self.screen = pygame.display.set_mode(self.SIZE, pygame.FULLSCREEN | pygame.DOUBLEBUF, 32)

		# self.screen = pygame.display.set_mode(self.SIZE, pygame.DOUBLEBUF, 32)

		pygame.display.set_caption("MRSL r-one Exhibit")

		self.background = pygame.Surface(self.screen.get_size())
		self.background.fill(Colors.OFFWHITE)

		riceImg = self.openImage("../../resources/rice.png")
		self.riceImg = self.scaleImageOnHeight(riceImg, 100)

		mrslImg = self.openImage("../../resources/mrsl.png")
		self.mrslImg = self.scaleImageOnHeight(mrslImg, 75)

		self.font = pygame.font.Font("freesansbold.ttf", 30)

	def openImage(self, filename):
		return pygame.image.load(filename).convert_alpha()

	def scaleImageOnHeight(self, image, height):
		x, y = image.get_size()
		aspect = float(x) / y
		size = (int(aspect * height), height)

		return pygame.transform.smoothscale(image, size)

	def drawSquares(self):
		SHADOW = 4
		PULSE = 2

		for index in xrange(4):
			if index == 0:
				if self.mode == 0:
					color = Colors.RED
				else:
					color = Colors.OFFRED

			elif index == 1:
				if self.mode == 1:
					color = Colors.GREEN
				else:
					color = Colors.OFFGREEN

			elif index == 2:
				if self.mode == 2:
					color = Colors.BLUE
				else:
					color = Colors.OFFBLUE

			elif index == 3:
				if self.mode == 3:
					color = Colors.YELLOW
				else:
					color = Colors.OFFYELLOW

			rect = [50, 125 + index * 85, 60, 60]

			rect[0] += SHADOW
			rect[1] += SHADOW

			if self.mode == index:
				c = 60 - self.oscillator * 30
				shadowColor = (c, c, c)
			else:
				shadowColor = Colors.OFFGREY
			pygame.draw.rect(self.screen, shadowColor, rect)

			rect[0] -= SHADOW
			rect[1] -= SHADOW

			if self.mode == index:
				rect[0] += self.oscillator * PULSE
				rect[1] += self.oscillator * PULSE

			pygame.draw.rect(self.screen, color, rect)

	def drawDialogBox(self):
		LW = 3

		# Draw 3 sides
		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(125, 115), (600, 115), LW)

		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(600, 115), (600, 450), LW)

		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(600, 450), (125, 450), 2)

		# Draw interesting sides
		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(40, 115 + self.mode * 84),
			(125, 115 + self.mode * 84),
			LW
		)

		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(40, 115 + (self.mode + 1) * 84 - 1),
			(125, 115 + (self.mode + 1) * 84 - 1),
			LW
		)

		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(40, 115 + self.mode * 84),
			(40, 115 + (self.mode + 1) * 84),
			LW
		)

		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(125, 115 + (self.mode + 1) * 84 - 1),
			(125, 450),
			LW
		)

		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(125, 115 + self.mode * 84),
			(125, 115),
			LW
		)

	def drawDialog(self):
		text = self.font.render("Follow the leader!", True, Colors.OFFBLACK)
		self.screen.blit(text, (135, 125))


	def updateDisplay(self):
		# Draw title bar
		self.screen.blit(self.background, (0, 0))
		self.screen.blit(self.riceImg, (15, 5))
		self.screen.blit(self.mrslImg, (640 - self.mrslImg.get_width() - 15, 10))

		# Draw separator bar
		pygame.draw.line(self.screen, Colors.OFFBLACK,
			(0, 100), (640, 100), 4)

		# Draw boxes
		self.drawSquares()

		# Draw dialog
		self.drawDialogBox()
		self.drawDialog()

		pygame.display.flip()


	def oscillatorUpdate(self):
		self.oscillator = math.sin(pygame.time.get_ticks() / 200.0)

	def _mainloop(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()

			self.updateDisplay()
			self.oscillatorUpdate()

			# self.mode += 1
			# self.mode %= 4

			self.clock.tick(FPS)

if __name__ == "__main__":
	display = Display()

	display._mainloop()