#!/usr/bin/python2
import os
import sys
import time
import threading

import msicontrolboard
import display2

if __name__ == "__main__":
	msiBoard = msicontrolboard.MSIControlBoard()
	msiBoard.start()

	if '-n' not in sys.argv:
		display = display2.Display(msiBoard)
		display.start()

	try:
		while True:
			pass

	except KeyboardInterrupt:
		msiBoard.stop()
		sys.exit(0)
