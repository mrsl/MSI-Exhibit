import os
import threading
import time
import glob
import math
import signal
import pygame
from pygame.locals import *

imagePrefix = "R-ONE SWARM_"

IDLE = 0
CLUSTER_ACTIVE = 1
CLUSTER_LOADING = 2
FLOCK_ACTIVE = 3
FLOCK_LOADING = 4
FOLLOW_ACTIVE = 5
FOLLOW_LOADING = 6

FPS = 10

class Display:
        SIZE = (1300, 700)

	mode = IDLE
	tick = 0

	def __init__(self, msiBoard):
		self.msiBoard = msiBoard

	def start(self):
		pygame.display.init()
		pygame.font.init()

		self.clock = pygame.time.Clock()

		# Set display mode
		self.screen = pygame.display.set_mode(
			self.SIZE,
			#pygame.FULLSCREEN | pygame.DOUBLEBUF,
			pygame.DOUBLEBUF,
			32
		)

                # Set size to screen's maximum size
		self.size = (
			pygame.display.Info().current_w,
			pygame.display.Info().current_h
		)

		# Hide mouse
		pygame.mouse.set_visible(False)

		# Open resources
		riceImg = self.openImage("resources/rice.png")
		self.riceImg = self.scaleImageOnHeight(riceImg, 100)

		mrslImg = self.openImage("resources/mrsl.png")
		self.mrslImg = self.scaleImageOnHeight(mrslImg, 75)

                attractImg = \
                    self.openImage("resources/" + imagePrefix + "attract.png")
                self.attractImg = \
                    self.scaleImageOnHeight(attractImg, self.size[1])

                clusteractiveImg = \
                    self.openImage("resources/" + imagePrefix + "cluster active.png")
                self.clusteractiveImg = \
                    self.scaleImageOnHeight(clusteractiveImg, self.size[1])

                clusterloadingImg = \
                    self.openImage("resources/" + imagePrefix + "cluster loading.png")
                self.clusterloadingImg = \
                    self.scaleImageOnHeight(clusterloadingImg, self.size[1])

                flockactiveImg = \
                    self.openImage("resources/" + imagePrefix + "flock active.png")
                self.flockactiveImg = \
                    self.scaleImageOnHeight(flockactiveImg, self.size[1])

                flockloadingImg = \
                    self.openImage("resources/" + imagePrefix + "flock loading.png")
                self.flockloadingImg = \
                    self.scaleImageOnHeight(flockloadingImg, self.size[1])

                followactiveImg = \
                    self.openImage("resources/" + imagePrefix + "follow active.png")
                self.followactiveImg = \
                    self.scaleImageOnHeight(followactiveImg, self.size[1])

                followloadingImg = \
                    self.openImage("resources/" + imagePrefix + "follow loading.png")
                self.followloadingImg = \
                    self.scaleImageOnHeight(followloadingImg, self.size[1])

                self._mainloop()

	def stop(self):
		self.active = False

	def openImage(self, filename):
		return pygame.image.load(filename).convert_alpha()

	def scaleImageOnHeight(self, image, height):
		x, y = image.get_size()
		aspect = float(x) / y
		size = (int(aspect * height), height)

		return pygame.transform.smoothscale(image, size)

        def updateDisplay(self):
                if self.mode == IDLE:
                        self.screen.blit(self.attractImg, (0, 0))
                elif self.mode == CLUSTER_ACTIVE:
                        self.screen.blit(self.clusteractiveImg, (0, 0))
                elif self.mode == CLUSTER_LOADING:
                        self.screen.blit(self.clusterloadingImg, (0, 0))
                elif self.mode == FLOCK_ACTIVE:
                        self.screen.blit(self.flockactiveImg, (0, 0))
                elif self.mode == FLOCK_LOADING:
                        self.screen.blit(self.flockloadingImg, (0, 0))
                elif self.mode == FOLLOW_ACTIVE:
                        self.screen.blit(self.followactiveImg, (0, 0))
                elif self.mode == FOLLOW_LOADING:
                        self.screen.blit(self.followloadingImg, (0, 0))

		pygame.display.flip()

        def _mainloop(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()

                        if (self.msiBoard):
                            self.mode = self.msiBoard.getMode()

                        else:
                            self.mode = IDLE

			self.updateDisplay()
			self.clock.tick(FPS)


if __name__ == "__main__":
	display = Display(None)
	display.start()
	display._mainloop()
