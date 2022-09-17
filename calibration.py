import math
import sys

# This example requires the PySide2 library for displaying windows and video. Other such libraries are avaliable, and
# you are free to use whatever you'd like for your projects.
from PySide2 import QtCore, QtGui, QtWidgets

import adhawkapi
import adhawkapi.frontend
from adhawkapi import MarkerSequenceMode, PacketType

def calibrate(self):
    ''' Runs a Calibration using AdHawk Backend's GUI '''

    # Two calibration modes are supported: FIXED_HEAD and FIXED_GAZE
    # With fixed head mode you look at calibration markers without moving your head
    # With fixed gaze mode you keep looking at a central point and move your head as instructed during calibration.
    self._api.start_calibration_gui(mode=MarkerSequenceMode.FIXED_HEAD, n_points=9, marker_size_mm=35,
                                    randomize=False, callback=(lambda *_args: None))

