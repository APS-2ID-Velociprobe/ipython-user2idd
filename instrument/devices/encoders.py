"""
external encoders -- interferometer data for sample stage

int_sam_x1	: 	2iddTAU:pmac1:m7.RBV
int_sam_y1	:	2iddTAU:pmac1:m8.RBV 

"""

__all__ = """
	int_sam_x1
	int_sam_y1
""".split()

from ..session_logs import logger

logger.info(__file__)

from ophyd import EpicsSignalRO

int_sam_x1 = EpicsSignalRO('2iddTAU:pmac1:m7.RBV', name='int_sam_x1')
int_sam_y1 = EpicsSignalRO('2iddTAU:pmac1:m8.RBV', name='int_sam_y1')
