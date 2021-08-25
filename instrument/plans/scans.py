"""
user-facing scans
"""

__all__ = """
    VPstepScan
    VPfermatSpiralStepScan
    VPspiralStepScan
    VPflyScan2d
    VPflyScan3d
""".split()

from bluesky.plan_stubs import mv
from bluesky.plans import grid_scan, spiral, spiral_fermat
from collections import OrderedDict
from ..utils.transforms import unCenterCoords
from ..devices.motors import *

import datetime
import os
import time

def VPstepScan(det, outer_center, outer_width, outer_step_size,
			   inner_center, inner_width, inner_step_size,
			   outer_motor = sm_py, 
			   inner_motor = sm_px, 
			   z_motor = sm_pz, z_pos = None, 
			   snake = True, md=None):
	'''
	args
	----
	det					:	list of detectors to acquire at each step
	outer_center		:	slow motor center position 
    outer_width			:	slow motor window width
    outer_step_size		:	slow motor step size
    inner_center		:	fast motor center position
    inner_width			:	fast motor window width
    inner_step_size		:	fast motor step size
			   
	kwargs
	------
	outer_motor = sm_py	: 	Slow motor defaults to sm_py 
	inner_motor = sm_px :	Fast motor defaults to sm_px
    z_motor = sm_pz		:	Z stage defaults to sm_pz - only used if 
							z_pos defined
    z_pos = None		:	Z position for scan 
    snake = True		:	"Snake'ing" the inner axis by default
    md = None			:	dictionary of optional metadata passed onto 
							grid_scan
	'''
	
	# coordinate transformation
	outer_start, outer_stop, outer_steps = unCenterCoords(outer_center, outer_width, outer_step_size)
	inner_start, inner_stop, inner_steps = unCenterCoords(inner_center, inner_width, inner_step_size)

	# move to start
	if z_pos is not None:
		yield from mv(outer_motor, outer_start, inner_motor, inner_start, z_motor, z_pos)
	else:
		yield from mv(outer_motor, outer_start, inner_motor, inner_start)
		
	# grid_scan
	yield from grid_scan(det, outer_motor, outer_start, outer_stop, outer_steps,
							inner_start, inner_stop, inner_steps, 
							snake_axes = snake, md=None)

	return


def VPfermatSpiralStepScan(det, x_center, y_center, x_radius, y_radius,
						delta_r, factor,
						outer_motor = sm_py, 
						inner_motor = sm_px, 
						delta_ry = None, tilt = 0.0,
						z_motor = sm_pz, z_pos = None, 
						md=None):
	'''
	args
	----
	det					:	list of detectors to acquire at each step
	x_center			:	x stage center position 
    y_center			:	y stage center position
    x_radius			:	half-width in x-direction
    y_radius			:	half-width in y-direction
    delta_r				:	delta radius along x-direction
    factor				:	radius is divided by factir
			   
	kwargs
	------
	delta_ry = None		:	delta radius along y-direction
	tilt = 0.0			:	tilt angle in radians
	x_motor = sm_px		: 	X stage defaults to sm_px 
	y_motor = sm_py 	:	Y stage defaults to sm_py
    z_motor = sm_pz		:	Z stage defaults to sm_pz - only used if 
							z_pos defined
    z_pos = None		:	Z position for scan 
    md = None			:	dictionary of optional metadata passed onto 
							grid_scan
	'''

	x_diameter = x_radius * 2.0
	y_diameter = y_radius * 2.0

	if z_pos is not None:
		yield from mv(x_motor, x_center, y_motor, y_center, z_motor, z_pos)
	else:
		yield from mv(x_motor, x_center, y_motor, y_center)
	
	# fermat_spiral_scan yield
	yield from spiral_fermat(det, x_motor, y_motor, x_center, y_center,
							 x_diameter, y_diameter, delta_r, dr_y = delta_ry,
							 tilt = tilt, md = md)

	return
	
def VPspiralStepScan(det, x_center, y_center, x_radius, y_radius,
						delta_r, n_theta,
						outer_motor = sm_py, 
						inner_motor = sm_px, 
						delta_ry = None, tilt = 0.0,
						z_motor = sm_pz, z_pos = None, 
						md=None):
	'''
	args
	----
	det					:	list of detectors to acquire at each step
	x_center			:	x stage center position 
    y_center			:	y stage center position
    x_radius			:	half-width in x-direction
    y_radius			:	half-width in y-direction
    delta_r				:	delta radius along x-direction
    n_theta				:	number of theta steps
			   
	kwargs
	------
	delta_ry = None		:	delta radius along y-direction 
	tilt = 0.0			:	tilt angle in radians
	x_motor = sm_px		: 	X stage defaults to sm_px 
	y_motor = sm_py 	:	Y stage defaults to sm_py
    z_motor = sm_pz		:	Z stage defaults to sm_pz - only used if 
							z_pos defined
    z_pos = None		:	Z position for scan 
    md = None			:	dictionary of optional metadata passed onto 
							grid_scan
	'''

	x_diameter = x_radius * 2.0
	y_diameter = y_radius * 2.0

	if z_pos is not None:
		yield from mv(x_motor, x_center, y_motor, y_center, z_motor, z_pos)
	else:
		yield from mv(x_motor, x_center, y_motor, y_center)
	
	# fermat_spiral_scan yield
	yield from spiral(det, x_motor, y_motor, x_center, y_center,
							 x_diameter, y_diameter, delta_r, n_theta,
							 dr_y = delta_ry, tilt = tilt, md = md)

	return












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
