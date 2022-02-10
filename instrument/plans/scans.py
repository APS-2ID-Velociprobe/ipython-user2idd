"""
user-facing scans
"""

__all__ = """
	VPstepScan
	VPfermatSpiralStepScan
	VPspiralStepScan
	VPcorrectedFermatSpiralStepScan
""".split()

from bluesky.plan_stubs import mv
from bluesky.plans import grid_scan, spiral, spiral_fermat, list_scan
from collections import OrderedDict
from ..utils.trajectory_tools import unCenterCoords, path_length, vogel_spiral, reorder_spiral_path, snaked_spiral_path
from ..devices.motors import *

import datetime
import os
import time
import numpy as np

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
							inner_motor, inner_start, inner_stop, inner_steps, 
							snake_axes = snake, md=None)

	return


def VPfermatSpiralStepScan(det, x_center, y_center, x_radius, y_radius,
						delta_r, factor,
						y_motor = sm_py, 
						x_motor = sm_px, 
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
	inner_motor = sm_px : 	inner stage defaults to sm_px 
	outer_motor = sm_py :	outer stage defaults to sm_py
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
							 x_diameter, y_diameter, delta_r, factor=factor, dr_y = delta_ry,
							 tilt = tilt, md = md)

	return
	
def VPspiralStepScan(det, x_center, y_center, x_radius, y_radius,
						delta_r, n_theta,
						y_motor = sm_py, 
						x_motor = sm_px, 
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
	outer_motor = sm_px	: 	inner stage defaults to sm_px 
	inner_motor = sm_py :	outer stage defaults to sm_py
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
	
	# grid_scan yield
	yield from spiral(det, x_motor, y_motor, x_center, y_center,
							 x_diameter, y_diameter, delta_r, n_theta,
							 dr_y = delta_ry, tilt = tilt, md = md)

	return


def VPcorrectedFermatSpiralStepScan(det, x_center, y_center, x_radius, y_radius,
									delta_r,
									y_motor = sm_py, 
									x_motor = sm_px, 
									z_motor = sm_pz, z_pos = None,
									factor = 1,
									rough_dr = 5,  
									snaked = False, polar=True, strips = 10, 
									md=None):
	'''
	args
	----
	det					:	list of detectors to acquire at each step
	x_center			:	x stage center position 
	y_center			:	y stage center position
	x_radius			:	half-width in x-direction
	y_radius			:	half-width in y-direction
	delta_r				:	delta radius along both x-,y-directions
 			   
	kwargs
	------
	inner_motor = sm_px : 	inner stage defaults to sm_px 
	outer_motor = sm_py :	outer stage defaults to sm_py
	z_motor = sm_pz		:	Z stage defaults to sm_pz - only used if 
							z_pos defined
	z_pos = None		:	Z position for scan 
	factor = 1			:	Used in fermat spiral point calculation
	rough_dr = 5		:	Used in forcing fermat spiral points into
							spiral-like ordering. This faux spiral has
							dr = rough_dr
	snaked - False		:	Ordering -- False --> spiral-like; True --> snake
							For snake scane, fast axis would be the 
							that defined by the inner_motor
	strips = 10			:	Used in forcing fermat spiral points into 
							snake like ordering.  Number of outer_motor levels
	md = None			:	dictionary of optional metadata passed onto 
							grid_scan
	'''

	r, theta = vogel_spiral(delta_r, x_radius, y_radius, factor, theta_0 = 137.508, polar = polar)

	if not snaked:
		trajectory_pol = reorder_spiral_path(r, theta, rough_dr)
		trajectory_cart = np.vstack((trajectory_pol[:,0]*np.cos(trajectory_pol[:,1]),trajectory_pol[:,0]*np.sin(trajectory_pol[:,1]))).T
	else:
		trajectory_cart = snaked_spiral_path(r, theta, strips = 10, snakeXaxis = True)		

	x_points = (trajectory_cart[:,0] + x_center).tolist()
	y_points = (trajectory_cart[:,1] + y_center).tolist()


	if z_pos is not None:
		yield from mv(x_motor, x_points[0], y_motor, y_points[0], z_motor, z_pos)
	else:
		yield from mv(x_motor, x_points[0], y_motor, y_points[0])


	# For live plots need dimensions added to metadata, which doesn't occur 
	# for list scans
	
	_md = {
		   'extents': tuple([[x_center - x_radius*1.25, x_center + x_radius*1.25],
							 [y_center - y_radius*1.25, y_center + y_radius*1.25]]),
		   'hints': {},
		   }
	try:
		dimensions = [(x_motor.hints['fields'], 'primary'),
					  (y_motor.hints['fields'], 'primary')]
	except (AttributeError, KeyError):
		pass
	else:
		_md['hints'].update({'dimensions': dimensions})
	_md.update(md or {})

	# fermat_spiral_scan yield
	yield from list_scan(det, x_motor, x_points, y_motor, y_points, md = _md)

	return





