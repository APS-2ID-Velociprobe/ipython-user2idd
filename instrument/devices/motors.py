"""
Velociprobe motors

M. Wyman 2021-07-19
"""

__all__ = """
	sm_px
	sm_py
	sm_pz
	sm_theta       
	xmotor
	ymotor
    soft_m4
	soft_m5
	pmac_m6
	pmac_m7
	pmac_m8
""".split()

from ..session_logs import logger

logger.info(__file__)

from ophyd import EpicsMotor


# m1 = EpicsMotor("ioc:m1", name="m1", labels=("motor",))
# m2 = EpicsMotor("ioc:m2", name="m2", labels=("motor",))
# m3 = EpicsMotor("ioc:m3", name="m3", labels=("motor",))
# m4 = EpicsMotor("ioc:m4", name="m4", labels=("motor",))
# tth = EpicsMotor("ioc:m5", name="tth", labels=("motor",))
# th = EpicsMotor("ioc:m6", name="th", labels=("motor",))
# chi = EpicsMotor("ioc:m7", name="chi", labels=("motor",))
# phi = EpicsMotor("ioc:m8", name="phi", labels=("motor",))

# sample motors
sm_px = EpicsMotor("2iddTAU:pmac1:M16", name="sm_px", labels=("motor",))
sm_py = EpicsMotor("2iddTAU:pmac1:M15", name="sm_py", labels=("motor",))
sm_pz = EpicsMotor("2iddVELO:m9", name="sm_pz", labels=("motor",))

# commented out in 2-d step scan	
# sm_theta = EpicsMotor("2iddf:m3", name="sm_theta", labels=("motor",))

# used in 2D/3D flyscan			
sm_theta = EpicsMotor("2iddVELO:m10", name="sm_theta", labels=("motor",))

# used in spiral scan
xmotor = EpicsMotor("2iddVELO:m1", name="xmotor", labels=("motor",))
ymotor = EpicsMotor("2iddVELO:m2", name="ymotor", labels=("motor",))

# Other motors
# 2iddf:sm4.VAL
#EpicsMotor("2iddf:sm4", name="sm4", labels=("motor",))

# 2iddf:sm5.VAL
#EpicsMotor("2iddf:sm5", name="sm5", labels=("motor",))

# 2iddf:sm4.RBV
soft_m4 = EpicsMotor("2iddf:sm4", name="sm4", labels=("motor",))

# 2iddf:sm5.RBV --> 
soft_m5 = EpicsMotor("2iddf:sm5", name="sm5", labels=("motor",))

# 2iddTAU:pmac1:m6.RBV
pmac_m6 = EpicsMotor("2iddTAU:pmac1:m6", name="pmac_m6", labels=("motor",))

# 2iddTAU:pmac1:m7.RBV
pmac_m7 = EpicsMotor("2iddTAU:pmac1:m7", name="pmac_m7", labels=("motor",))

# 2iddTAU:pmac1:m8.RBV
pmac_m8 = EpicsMotor("2iddTAU:pmac1:m8", name="pmac_m8", labels=("motor",))


