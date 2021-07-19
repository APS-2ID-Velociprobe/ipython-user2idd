"""
user-facing scans
"""

__all__ = """
    VPstepScan
    VPspiralScan
    VPflyScan2d
    VPflyScan3d
""".split()

#from apstools.devices import SCALER_AUTOCOUNT_MODE
from bluesky import plan_stubs as bps
from collections import OrderedDict
import datetime
import os
import time

#TODO
def VPstepScan(x, y, thickness_mm, title, md=None):
	'''
	[angle, X-pos, Y-pos, Z-pos, X-width, Y-width, X-step-um, Y-step-um, frequency]
	'''

#TODO
def VPspiralScan(xmotor='2iddVELO:m1', xLow=-1.0, xHigh=1.0, sepDist=.04
	            , dwell_s=0.2, ymotor='2iddVELO:m2', yLow=-1.0, yHigh=1.0
	            , camera='p300K:cam1:', debug=0, md=None):
	pass

#TODO	
def VPflyScan2d(pos_X, pos_Y, thickness, scan_title, md=None):
	'''
	scans [x-center(um) y-center.(um), z-position (um), x-width.(um)
	, y-width.(um), x-stepsize.(nm), Y-stepsize.(nm), Freq.(Hz)]
	'''
	pass

#TODO		
def VPflyScan3d(pos_X, pos_Y, thickness, scan_title, md=None):	
	'''
	scans [x-center(um) y-center.(um), z-position (um), x-width.(um)
	      , y-width.(um), x-stepsize.(nm), Y-stepsize.(nm), Freq.(Hz)]
	'''
	pass
