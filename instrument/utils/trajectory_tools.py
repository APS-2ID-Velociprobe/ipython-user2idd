""" Trajectory Tools """

__all__ = ['unCenterCoords',
		   'path_lengths',
		   'vogel_sprial',
		   'reorder_spiral_path',
		   'snaked_spiral_path']

import math
import numpy as np


def unCenterCoords(center, width, stepSize):
	"""
	Takes user coordinates (center, width, stepSize) and transforms
	to bluesky scan coordinates (start, stop, Nsteps)

	args
	----
	center		: float of scan center
	width		: float of scan width
	stepSize	: float of step size

	"""

	Nsteps = math.ceil(width/stepSize) + 1
	start = center-Nsteps/2.0*stepSize
	stop = center+Nsteps/2.0*stepSize
	
	return start, stop, Nsteps




def path_length(x, y):
	"""
	args
	----
	x	: ndarray of x-coordinates of trajectory
	y	: ndarray of y-coordinates of trajectory
	"""
	
	xx = x-np.roll(x,1)
	yy = y-np.roll(y,1)

	return np.sum(np.sqrt(xx**2+yy**2))-np.sqrt(xx[0]**2+yy[0]**2)




def vogel_spiral(dr, x_radius, y_radius, factor, theta_0 = 137.508, polar = False):
	"""
	args
	----
	dr					: float of radius step
	x_radius			: float of x_radius (half-width)
	y_radius			: float of y_radius (half-height)
	factor				: float of numer of turns per dr
	
	kwargs
	------
	theta_0 = 137.508	: float of angle (in degrees) between subsequent 
						  points in fermat spiral
	polar = False		: boolean to set output coordinate system: True -->
						  polar (r, theta); False --> cartesian (x,y)
	"""
	diag = np.sqrt(x_radius**2+y_radius**2)
	#num_rings = int((1.5*diag/(dr/factor))**2)
	num_rings = int((1.5*diag/(dr/factor))**2)/4 #by JD

	theta_rad = theta_0 * math.pi / 180.0
	#n = np.arange(num_rings)+1
	n = np.arange(num_rings+1) #by JD

	theta = theta_rad*n
	#r = dr*np.sqrt(n)  
	r = dr/factor*np.sqrt(n)  #by JD
	
	if not polar:
		x = r*np.cos(theta)
		y = r*np.sin(theta)
		return x, y
	else:
		return r, theta




def reorder_spiral_path(r, theta, dr): 
	"""
	args
	----
	r		: ndarray of radii in fermat trajectory
	theta	: ndarray of angles in fermat trajectory
	dr		: float of dr to use for "enforced" spiral
	"""
	
	coords_n = np.floor(r/dr).astype(int)
	
	if max(abs(theta)) > 2*math.pi:
		ttheta = theta % (2*math.pi)
	else:
		ttheta = theta
		
	for n in range(0,max(coords_n)+1):
		rs = r[coords_n == n]
		thetas = ttheta[coords_n == n]
		_spiraled = []
		for rr, tt in zip(rs, thetas):
			_spiraled.append([rr,tt])
		_spiraled_sorted = sorted(_spiraled, key=lambda coord: coord[1])
		if n == 0:
			spiraled = np.asarray(_spiraled_sorted)
		else:
			spiraled = np.append(spiraled, np.asarray(_spiraled_sorted), axis = 0)
			
	return spiraled




def snaked_spiral_path(r, theta, strips = 10, snakeXaxis = True): 
	"""
	args
	----
	r					: ndarray of radii in fermat trajectory
	theta				: ndarray of angles in fermat trajectory

	kwargs
	------
	strips = 10			: float of snake turns to make
	snakeXaxis	= True	: boolean of whether to snake x or y axis
	"""
	
	if snakeXaxis:
		xs = r*np.cos(theta)
		ys = r*np.sin(theta)
	else: 
		ys = r*np.cos(theta)
		xs = r*np.sin(theta)
	
	miny, maxy = np.min(ys), np.max(ys)
	dy = (maxy - miny)/strips
	
	ysteps = np.linspace(start = maxy, stop = miny, num = strips + 1)
	
	ystep_n = np.floor((maxy - ys)/dy).astype(int)
	
	for n in range(0, strips):
		xs_strip = xs[ystep_n == n]
		ys_strip = ys[ystep_n == n]
		_strip_pts = []
		for xx, yy in zip(xs_strip, ys_strip):
			_strip_pts.append([xx,yy])
		_strip_sorted = sorted(_strip_pts, key = lambda coord: coord[0])
		if n % 2 == 1:
			_strip_sorted.reverse()
		if n == 0:
			snaked = np.asarray(_strip_sorted)
		else:
			snaked = np.append(snaked, np.asarray(_strip_sorted), axis = 0)

	if not snakeXaxis:
		snaked[:,[0,1]] = snaked[:,[1,0]]
		
	return snaked
