"""
Velociprobe fly scanning plans

M. Wyman 2022-02-11
"""

import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from ..utils.trajectory_tools import unCenterCoords
from ..utils.file_tools import create_dir
from ..devices.motors import *
from ..devices.flyers import flyUserCalcEnable, scanUserCalcEnable, laserFrequency, triggerFrequency

__all__ = """
    staged_fly
    VPBatchFly2d
    VPFlyScan2d
""".split()

def staged_fly(flyers, md = None):

    @bpp.stage_decorator(flyers)
    def inner_fly():
        yield from bp.fly(flyers, md = md)

    return (yield from inner_fly())

def VPBatchFly2d(flyer, scan_parms):
    '''
    How do ensure each scan in the batch gets its own uid?
    '''

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
                x_motor = sm_px, y_motor = sm_py,
                z_motor = sm_pz, z_pos = None, 
                theta_motor = sm_theta, theta_pos = None,
                trig_freq = 80.0, laser_freq = 5000, scan_mode = 0, 
                exposure_factor = 2,
                main_dir='/mnt/micdata2/velociprobe/2021-2/Luo',
                scan_num = None, 
                md=None):
    '''
    args
    ----
    vpFlyer         :   integrated detector and hardware controlled motion "Device"
                        Expected input is vpFlyer as defined in 2d_flyers.py
    x_center        :   x motor center position (in um)
    x_width         :   x motor window width (in um)
    x_step_size     :   x motor step size (in um)
    y_center        :   y motor center position (in um)
    y_width         :   y motor window width (in um)
    y_step_size     :   y motor step size (in um)

    kwargs
    ------
    x_motor = sm_py         :   x motor defaults to sm_px; used for non-fly motions
    y_motor = sm_px         :   y motor defaults to sm_py; used for non-fly motions
    z_motor = sm_pz         :   Z stage defaults to sm_pz - only used if
                                z_pos defined
    z_pos = None            :   Z position for scan
    theta_motor = sm_theta  :   Theta stage defaults to sm_theta - only used if
                                theta_pos defined
    sm_theta = None         :   Theta position for scan
	trig_freq = 80 Hz		: 	Detector trigger frequency also used by D-T to calc motor speeds
	laser_freq = 5 kHz		:	D-T position recording frequency
    scan_mode = 0           :   0-snake, 5-spiral, 7-lissajous
    main_dir 				: 	main directory for storing position data and images
    md = None               :   dictionary of optional metadata passed onto
                                grid_scan
    '''

    # Setting up calcs for fly scan
    flyUserCalcEnable.put(1)
    scanUserCalcEnable.put(0)

    # Needs to be set for the PMAC to get the correct values
    vpFlyer.scan_width.put(x_width)
    vpFlyer.scan_height.put(y_width)
    vpFlyer.x_center.put(x_center)
    vpFlyer.y_center.put(y_center)
    vpFlyer.x_step_size.put(1000.0*x_step_size) # convert to nm
    vpFlyer.y_step_size.put(1000.0*y_step_size) # convert to nm

    # coordinate transformation
    x_start, x_stop, x_points = unCenterCoords(x_center, x_width, x_step_size)
    y_start, y_stop, y_points = unCenterCoords(y_center, y_width, y_step_size)

    N_points = x_points*y_points*1.5 

    #Velociprobe IOC calcs
    vpFlyer.scan_mode.put(scan_mode)

    #Eiger setup
    exposure_period = 1./trig_freq
    vpFlyer.cam_acquire_period.put(exposure_period)
    vpFlyer.cam_acquire_time.put(exposure_period/exposure_factor)
    if theta_pos is not None:
        vpFlyer.cam_chi_start.put(theta_pos)
    vpFlyer.cam_num_images.put(N_points)
    vpFlyer.cam_num_images_per_file.put(min([N_points,100000])) 


	#File saving
    if scan_num is None:
        pass

    scan_dir='/local/home/dpuser/'+main_dir.split('mic')[1]+'/ptycho/fly{:03d}'.format(scan_num)
    create_dir(main_dir+'/ptycho/fly{:03d}'.format(scan_num))

    vpFlyer.cam_filepath.put(scan_dir)
    vpFlyer.cam_FW_pattern.put('fly{:03d}'.format(scan_num))
    vpFlyer.scan_wf_1000.put(main_dir+'/positions')
    vpFlyer.scan_wf_1128.put('fly{:03d}'.format(scan_num))

    #what setup needs done? Eiger settings; pmac settings;
    #Laser frequency needs to be capped at 15 kHz
    laserFrequency.put(min([laser_freq,15000]))
    triggerFrequency.put(trig_freq)



    # move to start
    if z_pos is None and theta_pos is None:
        yield from bps.mv(x_motor, x_start, y_motor, y_start)
    elif z_pos is None and theta_pos is not None:
        yield from bps.mv(x_motor, x_start, y_motor, y_start, theta_motor, theta_pos)
    elif z_pos is not None and theta_pos is None:
        yield from bps.mv(x_motor, x_start, y_motor, y_start, z_motor, z_pos)
    else:
        yield from bps.mv(x_motor, x_start, y_motor, y_start, z_motor, z_pos, theta_motor, theta_pos)

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
#   else:
#       _md['hints'].update({'dimensions': dimensions})
    _md.update(md or {})
#       pass

    yield from staged_fly([vpFlyer], md = _md)

    return
