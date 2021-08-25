""" Coordinate Transformations """

__all__ = ['unCenterCoords']

import math


def unCenterCoords(center, width, stepSize):
	"""
	Takes user coordinates (center, width, stepSize) and transforms
	to bluesky scan coordinates (start, stop, Nsteps)
	"""

	Nsteps = math.ceil(width/stepSize) + 1
	start = center-Nsteps/2.0*stepSize
	stop = center+Nsteps/2.0*stepSize
	
	return start, stop, Nsteps
