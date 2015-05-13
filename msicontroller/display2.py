import os
import threading
import time
import glob
import math
import signal
import pygame
from pygame.locals import *

imagePrefix = "R-ONE SWARM_"
# imageDir = "/home/mrsl/MSI-Exhibit/msicontroller/resources/"
imageDir = "/home/zkk/arch/zkk/mrsl/MSI-Exhibit/msicontroller/resources/"

IDLE = 0
CLUSTER_ACTIVE = 1
CLUSTER_LOADING = 2
FLOCK_ACTIVE = 3
FLOCK_LOADING = 4
FOLLOW_ACTIVE = 5
FOLLOW_LOADING = 6

FPS = 10

class Display:
        SIZE = (656, 512)

	mode = IDLE
	tick = 0

	def __init__(self, msiBoard):
		self.msiBoard = msiBoard

	def start(self):
		pygame.display.init()

		print "Initializing display"

		self.clock = pygame.time.Clock()

		# Set display mode
		self.screen = pygame.display.set_mode(
			self.SIZE,
			# pygame.FULLSCREEN | pygame.DOUBLEBUF,
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
                attractImg = \
                    self.openImage(imageDir + imagePrefix + "attract.png")
                self.attractImg = \
                    self.scaleImageOnHeight(attractImg, self.size[1])

                clusteractiveImg = \
                    self.openImage(imageDir + imagePrefix + "cluster active.png")
                self.clusteractiveImg = \
                    self.scaleImageOnHeight(clusteractiveImg, self.size[1])

                clusterloadingImg = \
                    self.openImage(imageDir + imagePrefix + "cluster loading.png")
                self.clusterloadingImg = \
                    self.scaleImageOnHeight(clusterloadingImg, self.size[1])

                flockactiveImg = \
                    self.openImage(imageDir + imagePrefix + "flock active.png")
                self.flockactiveImg = \
                    self.scaleImageOnHeight(flockactiveImg, self.size[1])

                flockloadingImg = \
                    self.openImage(imageDir + imagePrefix + "flock loading.png")
                self.flockloadingImg = \
                    self.scaleImageOnHeight(flockloadingImg, self.size[1])

                followactiveImg = \
                    self.openImage(imageDir + imagePrefix + "follow active.png")
                self.followactiveImg = \
                    self.scaleImageOnHeight(followactiveImg, self.size[1])

                followloadingImg = \
                    self.openImage(imageDir + imagePrefix + "follow loading.png")
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

	def scaleImage(self, image, size):
		x, y = image.get_size()
		aspect = float(x) / y
		size = (int(aspect * height), int(aspect * width))

		return pygame.transform.smoothscale(image, size)

        def updateDisplay(self):
                size = self.attractImg.get_size()
                offset = tuple(-i / 2 for i in size)
                center = tuple(i / 2 for i in self.size)
                draw = tuple(offset[i] + center[i] for i in xrange(2))

                if self.mode == IDLE:
                        self.screen.blit(self.attractImg, draw)
                elif self.mode == CLUSTER_ACTIVE:
                        self.screen.blit(self.clusteractiveImg, draw)
                elif self.mode == CLUSTER_LOADING:
                        self.screen.blit(self.clusterloadingImg, draw)
                elif self.mode == FLOCK_ACTIVE:
                        self.screen.blit(self.flockactiveImg, draw)
                elif self.mode == FLOCK_LOADING:
                        self.screen.blit(self.flockloadingImg, draw)
                elif self.mode == FOLLOW_ACTIVE:
                        self.screen.blit(self.followactiveImg, draw)
                elif self.mode == FOLLOW_LOADING:
                        self.screen.blit(self.followloadingImg, draw)

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
