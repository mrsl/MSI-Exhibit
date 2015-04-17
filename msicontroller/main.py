#!/usr/bin/python2
import os
import sys
import time
import threading

import msicontrolboard
import display

if __name__ == "__main__":
	msiBoard = msicontrolboard.MSIControlBoard()
	msiBoard.start()

	# display = display.Display(msiBoard)
	# display.start()

	try:
		while True:
			pass

	except KeyboardInterrupt:
		msiBoard.stop()
		sys.exit(0)
