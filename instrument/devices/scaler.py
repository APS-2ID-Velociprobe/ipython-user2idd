"""
example scaler
"""

__all__ = """
	scaler1
	scaler1f
	s3
	s4
	s5
	s2f
	s3f
	s4f
	s5f
	s7f
""".split()

from ..session_logs import logger

logger.info(__file__)

from ophyd.scaler import ScalerCH
from ophyd import Kind

# # make an instance of the entire scaler, for general control
# scaler1 = ScalerCH("ioc:scaler1", name="scaler1", labels=["scalers", "detectors"])

scaler1 = ScalerCH("2idd:scaler1", name="scaler1", labels=["scalers", "detectors"])
scaler1f = ScalerCH("2iddf:scaler1", name="scaler1f", labels=["scalers", "detectors"])


# # choose just the channels with EPICS names
# scaler1.select_channels()

# # examples: make shortcuts to specific channels assigned in EPICS

# timebase = scaler1.channels.chan01.s
# I0 = scaler1.channels.chan02.s
# scint = scaler1.channels.chan03.s
# diode = scaler1.channels.chan04.s

s3 = scaler1.channels.chan03.s
s4 = scaler1.channels.chan04.s
s5 = scaler1.channels.chan05.s

s2f = scaler1f.channels.chan02.s
s3f = scaler1f.channels.chan03.s
s4f = scaler1f.channels.chan04.s
s5f = scaler1f.channels.chan05.s
s7f = scaler1f.channels.chan07.s

# for item in (timebase, I0, scint, diode):
#     item._ophyd_labels_ = set(["channel", "counter",])
