#!/usr/bin/python2
import os
import sys
import time
import threading

import msicontrolboard

if __name__ == "__main__":
	msiBoard = msicontrolboard.MSIControlBoard()
	msiBoard.start()

	# Busy wait
	try:
		while True:
			pass

	except KeyboardInterrupt:
		msiBoard.stop()
		sys.exit(0)