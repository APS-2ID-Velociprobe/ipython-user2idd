"""
Velociprobe fly scanning devices

M. Wyman 2022-02-08
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
    vpFlyer
""".split()


'''
PUt in devices and will want to add to init: "from 2d_flyers import *"
'''

# fly scan usercalc enable
flyUserCalcEnable = EpicsSignal('2iddVELO:userCalcEnable.VAL')
# step scan usercalc enable
scanUserCalcEnable = EpicsSignal('2iddf:userCalcEnable.VAL')
# laser Frequency
laserFrequency = EpicsSignal('2iddVELO:afg:set_freq', name = "laser_freq")

'''
Using https://github.com/APS-2BM-MIC/ipython-user2bmb/blob/e0e601c84f41163ce3f08d88cb24b7e66a0ca65c/profile_2bmb/startup/taxi_and_fly.ipynb
as template
'''

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
eiger_FW_enable_PV =
eiger_SaveFiles_PV =
eiger_FW_auto_rm_PV =
eiger_filepath_PV =
eiger_FW_pattern_PV =


class PmacEigerFlyer(Device):


    def __init__(self, pmac_pv, eiger_pv, acro_pv, *args, **kwargs  ):

        super().__init__('', parent=None, **kwargs)
        self.complete_status = None

        monitor = EpicsSignalRO(acro_pv, name = "monitor")
        scan_trigger = EpicsSignal(pmac_pv+trigger_PV, name = "scan_trigger")
        scan_mode = EpicsSignal(pmac_pv+mode_PV, name = "scan_mode")
        cam_acquire = EpicsSignal(eiger_pv+acquisition_PV, name = "cam_acquire")
        cam_trigger_mode = EpicsSignal(eiger_pv+trigger_mode_PV, name = "cam_trigger_mode")
        cam_manual_trigger = EpicsSignal(eiger_pv+manual_trigger_PV, name = "cam_manual_trigger")
        cam_num_triggers = EpicsSignal(eiger_pvnum_triggers_PV, name = "cam_num_triggers")

        scan_width = EpicsSignal('2iddVELO:VP:ScanWidth.VAL', "scan width")
        scan_height = EpicsSignal('2iddVELO:VP:ScanHeight.VAL', "scan height")
        x_center =  EpicsSignal('2iddVELO:VP:X_Center.VAL', "x_center")
        y_center = EpicsSignal('2iddVELO:VP:Y_Center.VAL', "y_center")
        x_step_size = EpicsSignal('2iddVELO:VP:X_Step_Size.VAL', "x_step_size")
        y_step_size = EpicsSignal('2iddVELO:VP:Y_Step_Size.VAL', "y_step_size")

        self.stage_sigs['cam_trigger_mode'] = 0
        self.stage_sigs['cam_manual_trigger'] = 0
        self.stage_sigs['cam_num_triggers'] = 1

    def kickoff(self):
            """
            Start this Flyer
            """
#           logger.info("kickoff()")
            self.complete_status = DeviceStatus(self)

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

            self.monitor.subscribe(cb)
#            self.cam_acquire.subscribe(cb)

            # set kickoff status to done
            kickoff_status = DeviceStatus(self)
            kickoff_status._finished(success=True)
            return kickoff_status

    def complete(self):
        """
        Wait for flying to be complete
        """
#        logger.info("complete(): " + str(self.complete_status))
        return self.complete_status

    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        """
#        logger.info("describe_collect()")
        schema = {}
        # TODO: What will be returned?
        return {self.name: schema}

    def collect(self):
        """
        Start this Flyer
        """
        # logger.info("collect(): " + str(self.complete_status))
        self.cam_acquire.put(0)
        self.complete_status = None
        # TODO: What will be yielded?
        d = {}

        yield d



vpFlyer = PmacEigerFlyer(name = 'vpFlyer')
