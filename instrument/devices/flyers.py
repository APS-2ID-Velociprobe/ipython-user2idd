"""
Velociprobe fly scanning devices

M. Wyman 2022-02-08
"""

from ophyd import Device, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
import logging
from ... import flyer #????

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

# Laser frequency
laserFrequency = EpicsSignal('2iddVELO:afg:set_freq')

'''
Using https://github.com/APS-2BM-MIC/ipython-user2bmb/blob/e0e601c84f41163ce3f08d88cb24b7e66a0ca65c/profile_2bmb/startup/taxi_and_fly.ipynb
as template
'''




class PmacEigerFlyer(Device):

	def __init__(self, monitor_PV = '2iddf:9440:1:bi_1.VAL',
				  mode_PV = '2iddTAU:pmac1:Motion_Program',
				  trigger_PV = '2iddTAU:pmac1:Calc_Motion_Cmd.PROC',
				  acquire_PV = 'dp_eiger_xrd91:cam1:Acquire' ):

		super().__init__('', parent=None, **kwargs)
        self.complete_status = None

		self.monitor_PV = monitor_PV
		self.mode_PV = mode_PV
		self.trigger_PV = trigger_PV
		self.acquire_PV = acquire_PV

		self.monitor = EpicsSignalRO(self.monitor_PV) # != 1 not scanning, == 1 scanning
		self.start_program = EpicsSignal(self.trigger_PV) # set to 1 to start
		self.mode = EpicsSignal(self.mode_PV) # generally set to 5 for snake scans
		self.cam_acquire = EpicsSignal(self.acquire_PV)

#		self.stage_sigs[self.user_offset] = 5

	def stage(self):
        print('FLyscan staged.')
        super().stage()

	def unstage(self):
        print('Flyscan unstaged.')
        super().unstage()

	def kickoff(self):
        	"""
        	Start this Flyer
       		 """
        	logger.info("kickoff()")
        	self.complete_status = DeviceStatus(self.busy)

			#trigger system
        	#self.busy.put(BusyStatus.busy) -- from example
			#send trigger to start_program
			self.start_program.put(1)
			while(self.monitor.get() != 1):
				print("waiting for pmac to begin")
				time.sleep(0.01)
			#send trigger to camera
			self.cam_acquire.put(1)

			#add callback functions to set complete after fly scan trajectory
			#and detector acquisition complete
        	def cb(*args, **kwargs):
            		if self.monitor.get() AND !self.cam_acquire.get():
                		self.complete_status._finished(success=True)

        	self.monitor.subscribe(cb)
			self.cam_acquire.subscribe(cb)

			# set kickoff status to done
        	kickoff_status = DeviceStatus(self)
        	kickoff_status._finished(success=True)
        	return kickoff_status

	def complete(self):
		"""
        Wait for flying to be complete
        """
        logger.info("complete(): " + str(self.complete_status))
		print("Fly scan completed")
        return self.complete_status

	def describe_collect(self):
		"""
        Describe details for ``collect()`` method
        """
        logger.info("describe_collect()")
        schema = {}
        # TODO: What will be returned?
        return {self.name: schema}

	def collect(self):
		"""
        Start this Flyer
        """
        logger.info("collect(): " + str(self.complete_status))
        self.complete_status = None
        # TODO: What will be yielded?

#	def unstage():

pmac_monitor_PV = '2iddf:9440:1:bi_1.VAL'
pmac_mode_PV = '2iddTAU:pmac1:Motion_Program'
pmac_trigger_PV = '2iddTAU:pmac1:Calc_Motion_Cmd.PROC'
eiger_acquisition_PV = 'dp_eiger_xrd91:cam1:Acquire'

vpFlyer = PmacEigerFlyer(monitor_PV = pmac_monitor_PV,
						 mode_PV = pmac_mode_PV,
						 trigger_PV = pmac_trigger_PV,
						 acquire_PV = eiger_acquisition_PV)
