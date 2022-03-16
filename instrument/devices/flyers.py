"""
Velociprobe fly scanning devices

M. Wyman 2022-02-11
"""

from ophyd import Device, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from ophyd.status import DeviceStatus

import time
import logging

__all__ = """
    flyUserCalcEnable
    scanUserCalcEnable
    laserFrequency
    triggerFrequency
""".split()

logger = logging.getLogger()

# fly scan usercalc enable
flyUserCalcEnable = EpicsSignal('2iddVELO:userCalcEnable.VAL')
# step scan usercalc enable
scanUserCalcEnable = EpicsSignal('2iddf:userCalcEnable.VAL')
# laser Frequency
laserFrequency = EpicsSignal('2iddVELO:afg:set_freq', name = "laser_frequency")
# detector trigger frequency also needed by D-T to calculate motor speeds
triggerFrequency = EpicsSignal('2iddVELO:VP:Trigger_Freq_Hz', name ="trigger_frequency")

# PV suffixese for eiger
pmac_mode_PV = 'Motion_Program' # generally set to 5 for snake scans
pmac_trigger_PV = 'Calc_Motion_Cmd.PROC' # set to 1 to start
pmac_wf_1000_PV = 'writeWF_1000.VAL'
pmac_wf_1128_PV = 'writeWF_1128.VAL'

# PV suffixes for eiger
eiger_acquisition_PV = 'cam1:Acquire'
eiger_trigger_mode_PV = 'cam1:TriggerMode' # set to 0 for fly scans
eiger_manual_trigger_PV = 'cam1:ManualTrigger' # set to 0 fly scans
eiger_num_triggers_PV = 'cam1:NumTriggers' # set to 1 for fly scans
eiger_acquire_period_PV = 'cam1:AcquirePeriod'
eiger_acquire_time_PV = 'cam1:AcquireTime'
eiger_chi_start_PV = 'cam1:ChiStart'
eiger_num_images_PV = 'cam1:NumImages'
eiger_num_images_per_file_PV = 'cam1:FWNImagesPerFile' 
eiger_FW_enable_PV = 'cam1:FWEnable'
eiger_SaveFiles_PV = 'cam1:SaveFiles'
eiger_FW_auto_rm_PV = 'cam1:FWAutoRemove'
eiger_filepath_PV = 'cam1:FilePath'
eiger_FW_pattern_PV = 'cam1:FWNamePattern'


class PmacEigerFlyer(Device):


    def __init__(self, pmac_pv, acro_pv, eiger_pv, *args, **kwargs  ):

        super().__init__('', parent=None, **kwargs)
        self.complete_status = None

        self.monitor = EpicsSignalRO(acro_pv, name = "monitor")
        
        self.scan_trigger = EpicsSignal(pmac_pv+pmac_trigger_PV, name = "scan_trigger")
        self.scan_mode = EpicsSignal(pmac_pv+pmac_mode_PV, name = "scan_mode")
        self.scan_wf_1000 = EpicsSignal(pmac_pv+pmac_wf_1000_PV, name = 'scan_wf_1000')
        self.scan_wf_1128 = EpicsSignal(pmac_pv+pmac_wf_1128_PV, name = 'scan_wf_1128')

        self.cam_acquire = EpicsSignal(eiger_pv+eiger_acquisition_PV, name = "cam_acquire")
        self.cam_trigger_mode = EpicsSignal(eiger_pv+eiger_trigger_mode_PV, name = "cam_trigger_mode")
        self.cam_manual_trigger = EpicsSignal(eiger_pv+eiger_manual_trigger_PV, name = "cam_manual_trigger")
        self.cam_num_triggers = EpicsSignal(eiger_pv+eiger_num_triggers_PV, name = "cam_num_triggers")
        self.cam_acquire_period = EpicsSignal(eiger_pv+eiger_acquire_period_PV, name = 'cam_acquire_period')
        self.cam_acquire_time = EpicsSignal(eiger_pv+eiger_acquire_time_PV, name = 'cam_acquire_time')
        self.cam_chi_start = EpicsSignal(eiger_pv+eiger_chi_start_PV, name = 'cam_chi_start')
        self.cam_num_images = EpicsSignal(eiger_pv+eiger_num_images_PV, name = 'cam_num_images')
        self.cam_num_images_per_file = EpicsSignal(eiger_pv+eiger_num_images_per_file_PV, name = 'cam_num_images_per_file') 
        self.cam_FW_enable = EpicsSignal(eiger_pv+eiger_FW_enable_PV, name = 'cam_FW_enable')
        self.cam_SaveFiles = EpicsSignal(eiger_pv+eiger_SaveFiles_PV, name = 'cam_SaveFiles')
        self.cam_FW_auto_rm = EpicsSignal(eiger_pv+eiger_FW_auto_rm_PV, name = 'cam_FW_auto_rm')
        self.cam_filepath = EpicsSignal(eiger_pv+eiger_filepath_PV, name = 'cam_filepath')
        self.cam_FW_pattern = EpicsSignal(eiger_pv+eiger_FW_pattern_PV, name = 'cam_FW_pattern')

        self.scan_width = EpicsSignal('2iddVELO:VP:ScanWidth.VAL', name = 'scan_width')
        self.scan_height = EpicsSignal('2iddVELO:VP:ScanHeight.VAL', name = 'scan_height')
        self.x_center =  EpicsSignal('2iddVELO:VP:X_Center.VAL', name = 'x_center')
        self.y_center = EpicsSignal('2iddVELO:VP:Y_Center.VAL', name = 'y_center')
        self.x_step_size = EpicsSignal('2iddVELO:VP:X_Step_Size.VAL', name = 'x_step_size')
        self.y_step_size = EpicsSignal('2iddVELO:VP:Y_Step_Size.VAL', name = 'y_step_size')

        self.stage_sigs['cam_trigger_mode'] = 0
        self.stage_sigs['cam_manual_trigger'] = 0
        self.stage_sigs['cam_num_triggers'] = 1
        self.stage_sigs['cam_FW_enable'] = 1 
        self.stage_sigs['cam_SaveFiles'] = 1
        self.stage_sigs['cam_FW_auto_rm'] = 1 

    def stage(self):
        super().stage()
        print('Flyer staged.')
 
    def unstage(self):
        super().unstage()

        self.monitor.unsubscribe(self.monitor_cb_index)

        print('Flyer unstaged.')


    def kickoff(self):
            """
            Start this Flyer
            """
#           logger.info("kickoff()")
            self.complete_status = DeviceStatus(self)

            self.start_time = time.time()

            #trigger system
            #self.busy.put(BusyStatus.busy) -- from example
            #send trigger to start_program
            self.scan_trigger.put(1)
            while(self.monitor.get() != 1):
                print("waiting for pmac to begin", end="\r")
                time.sleep(0.01)
            print("\nPMAC has started---------")

            #send trigger to camera
            self.cam_acquire.put(1)

            #add callback functions to set complete after fly scan trajectory
            #and detector acquisition complete
            def cb(*args, **kwargs):
                    if not self.monitor.get(): #and self.cam_acquire.get():
                        self.complete_status._finished(success=True)
                        self.cam_acquire.put(0)

            self.monitor_cb_index = self.monitor.subscribe(cb)
#            self.cam_acquire.subscribe(cb)

            # set kickoff status to done
            kickoff_status = DeviceStatus(self)
            kickoff_status._finished(success=True)
            return kickoff_status

    def complete(self):
        """
        Wait for flying to be complete
        """
        logger.info("complete(): " + str(self.complete_status))
        return self.complete_status

    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        """
        logger.info("describe_collect()")
        return {
            self.name: dict(
                ifly_xArr = dict(
                    source = self.positions.pvname,
                    dtype = "number",
                    shape = (1,)
                ),
                ifly_tArr = dict(
                    source = self.times.pvname,
                    dtype = "number",
                    shape = (1,)
                )
            )
        }

    def collect(self):
        """
        Start this Flyer
        """
        print("Storing data")
        logger.info("collect(): " + str(self.complete_status))
        
        self.end_time = time.time()
        
        self.cam_acquire.put(0)
        self.complete_status = None
        # only data being stored is start and end times of each flyscan
        t = [0,self.end_time-self.start_time]
        x = [0,self.cam_num_images.value]
        
        for i in range(2):
            d = dict(
                time=self.start_time + t[i],
                data=dict(
                    ifly_tArr = t[i],
                    ifly_xArr = x[i],
                ),
                timestamps=dict(
                    ifly_tArr = t[i],
                    ifly_xArr = t[i],
                )
            )
            yield d



