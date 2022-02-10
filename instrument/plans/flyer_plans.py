import bluesky.plans as bp
from bluesky.plan_stubs import mv
from bluesky.preprocessors import fly_during_wrapper
from ..utils.trajectory_tools import unCenterCoords
from ..devices.motors import *

__all__ = """
    staged_fly
    VPBatchFly2d
    VPFlyScan2d
""".split()

def staged_fly(flyers):

    @bpp.stage_decorator(flyers)
    def inner_fly():
        yield from bp.fly(flyers)

    return (yield from inner_fly())

def VPBatchFly2d(flyer, scan_parms):
    '''
    How do ensure each scan in the batch gets its own uid?
    '''
    #Velociprobe IOC calcs
    vpFlyer.mode.set(5)     # setting up for snake scan
    flyUserCalcEnable.put(1)
    scanUserCalcEnable.put(0)

    #Eiger setup
    #! caput ('dp_eiger_xrd91:cam1:FWEnable',1)
    #! caput ('dp_eiger_xrd91:cam1:SaveFiles',1)
    #! caput ('dp_eiger_xrd91:cam1:FWAutoRemove',1)

    #what setup needs done? Eiger settings; pmac settings;
    #! caput('2iddVELO:VP:Pause_Resume.VAL',1)
    #! gantry_z=caget('2iddf:Granite_Z:GoTo.VAL')

    for scan in scan_parms:
        #scans[-1] is the last element in the old scan list
        #! laser_freq=scan[-1]*pos_sampling
        #! trig_freq = np.min((15000,laser_freq))
        yield from VPFlyScan2d(flyer, scan_parms)

def VPFlyScan2d(vpFlyer, x_center, x_width, x_step_size,
               y_center, y_width, y_step_size,
               x_motor = sm_px,
               y_motor = sm_py,
               z_motor = sm_pz, z_pos = None,
               trig_freq = 80.0,
               md=None):
    '''
    args
    ----
    vpFlyer         :   integrated detector and hardware controlled motion "Device"
                        Expected input is vpFlyer as defined in 2d_flyers.py
    x_center        :   x motor center position
    x_width         :   x motor window width
    x_step_size     :   x motor step size
    y_center        :   y motor center position
    y_width         :   y motor window width
    y_step_size     :   y motor step size

    kwargs
    ------
    x_motor = sm_py     :   x motor defaults to sm_px; used for non-fly motions
    y_motor = sm_px     :   y motor defaults to sm_py; used for non-fly motions
    z_motor = sm_pz     :   Z stage defaults to sm_pz - only used if
                            z_pos defined (only for non-fly motions)
    z_pos = None        :   Z position for scan
    snake = True        :   "Snake'ing" the inner axis by default
    md = None           :   dictionary of optional metadata passed onto
                            grid_scan
    '''
    # Is this necessary???
    # coordinate transformation
    x_start, x_stop, _ = unCenterCoords(x_center, x_width, x_step_size)
    y_start, y_stop, _ = unCenterCoords(y_center, y_width, y_step_size)

    #Velociprobe IOC calcs

    #Eiger setup

    #what setup needs done? Eiger settings; pmac settings;
    laserFrequency.put(trig_freq)

    # move to start
    if z_pos is not None:
        yield from mv(x_motor, x_start, y_motor, y_start, z_motor, z_pos)
    else:
        yield from mv(x_motor, x_start, y_motor, y_start)

# Added commented-out code in case needed for callbacks. This version was used
# in VPcorrectedFermatSpiralStepScan
    _md = {}
#   _md = {
#          'extents': tuple([[x_center - x_radius*1.25, x_center + x_radius*1.25],
#                            [y_center - y_radius*1.25, y_center + y_radius*1.25]]),
#          'hints': {},
#          }
#   try:
#       dimensions = [(x_motor.hints['fields'], 'primary'),
#                     (y_motor.hints['fields'], 'primary')]
#   except (AttributeError, KeyError):
#       pass
#   else:
#       _md['hints'].update({'dimensions': dimensions})
    _md.update(md or {})

    yield from staged_fly([vpFlyer], md = _md)

    return
