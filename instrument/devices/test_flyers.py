"""
Velociprobe fly scanning devices -- possible template to follow

M. Wyman 2021-07-19
"""

__all__ = """
	testFlyer
""".split()

from ..session_logs import logger

logger.info(__file__)

from ophyd import DeviceStatus, Signal
from ophyd.flyers import FlyerInterface, AreaDetectorTimeseriesCollector, MonitorFlyerMixin

""" 

Working from Pete's sscan_1d_flyer example
https://github.com/BCDA-APS/bluesky_training/blob/main/sscan_1d_flyer.ipynb

"""

class deltaTau_flyer(FlyerInterface, SscanRecord):

    def __init__(self, *args, **kwargs):
        self._acquiring = False

        super().__init__(*args, **kwargs)

    def stage(self):
        super().stage()
        self.select_channels()

    def unstage(self):
        super().unstage()
        self.select_channels()

    def setup_staging_1D_step(self, start=-1.1, finish=1.1, num=21, ddelay=0.01, pdelay=0):
        """Configure sscan record for 1D step scan: noisy v. m1"""
        self.xref = dict(
            positioners=[m1, ],
            raw_detectors=[noisy, ],
            detectors=[noisy, m1.user_setpoint]  # include motor setpoints array
        )
        self.stage_sigs["number_points"] = num
        self.stage_sigs["pasm"] = "PRIOR POS"
        self.stage_sigs["positioner_delay"] = pdelay
        for i, p in enumerate(self.xref["positioners"]):
            self.stage_sigs[f"positioners.p{i+1}.setpoint_pv"] = p.user_setpoint.pvname
            self.stage_sigs[f"positioners.p{i+1}.readback_pv"] = p.user_readback.pvname
            self.stage_sigs[f"positioners.p{i+1}.start"] = start
            self.stage_sigs[f"positioners.p{i+1}.end"] = finish
        self.stage_sigs["detector_delay"] = ddelay
        for i, d in enumerate(self.xref["detectors"]):
            self.stage_sigs[f"detectors.d{i+1:02d}.input_pv"] = d.pvname

        # Get timestamp of each point in the scan.
        # This is a sscan record feature that returns the time since the scan started.
        # The time returned is relative to the first point of the scan.
        self.stage_sigs[f"positioners.p4.readback_pv"] = "time"  # or TIME (all upper case)

    def read_configuration(self):
        return {}

    def describe_configuration(self):
        return {}

    def kickoff(self):
        """Start the sscan record."""
        # self.setup_staging_1D_step()
        self.stage()
        time.sleep(0.1)

        # set(), do not `yield`, in kickoff()
        self.execute_scan.set(1)  # start the sscan record
        self._acquiring = True

        status = DeviceStatus(self)
        status.set_finished()  # means that kickoff was successful
        return status

    def complete(self):
        """Wait for sscan to complete."""
        logging.info("complete() starting")
        if not self._acquiring:
            raise RuntimeError("Not acquiring")

        st = DeviceStatus(self)
        cb_started = False

        def execute_scan_cb(value, timestamp, **kwargs):
            """Watch ``sscan.EXSC`` for completion."""
            value = int(value)
            if cb_started and value == 0:
                logging.info("complete() ending")
                self.unstage()
                self._acquiring = False
                self.execute_scan.unsubscribe(execute_scan_cb)
                if not st.done:
                    logging.info("Setting %s execute status to `done`.", self.name)
                    st.set_finished()

        self.execute_scan.subscribe(execute_scan_cb)
        # self.execute_scan.set(1)
        cb_started = True
        return st

    def describe_collect(self):
        """
        Provide schema & meta-data from collect().
        
        http://nsls-ii.github.io/ophyd/generated/ophyd.flyers.FlyerInterface.describe_collect.html
        """
        dd = {}
        dd.update(m1.describe())
        dd.update(noisy.describe())
        return {self.name: dd}

    def collect(self):
        """
        Retrieve all collected data (after complete()).
        
        Retrieve data from the flyer as proto-events.
        http://nsls-ii.github.io/ophyd/generated/ophyd.flyers.FlyerInterface.collect.html
        """
        if self._acquiring:
            raise RuntimeError("Acquisition still in progress. Call complete() first.")
        
        def get_data_from_sscan(obj, n):
            """Read a sscan array and return as Python list."""
            data = obj.read()[obj.name]
            data["value"] = list(data["value"][:n])
            return data

        def mkdoc(seq_num, values):
            """Bundle the dictionary of values into a raw event document."""
            timestamp = values.pop("__ts__")
            yield dict(
                seq_num=seq_num,
                time=timestamp,
                data={k: v for k, v in values.items()},
                timestamps={k: timestamp for k in values},
            )

        def read_sscan_data(scan):
            """Get the sscan arrays and yield as discrete events."""
            _cp = scan.current_point.read()[scan.current_point.name]
            n = _cp["value"]
            ts_last_point = _cp["timestamp"]

            # get the per-step time stamps from positioner 4
            ts_arr = self.positioners.p4.array.get(use_monitor=False)[:n]
            ts_arr = ts_last_point + ts_arr - ts_arr.max()

            results = dict(__ts__=list(ts_arr))  # __ts__ holds the timestamps, per point

            # This gets the full array for each item in one document
            for category, signals in scan.xref.items():
                for i, signal in enumerate(signals):
                    if category == "positioners":
                        item = f"p{i+1}"
                    elif category == "detectors":
                        item = f"d{i+1:02d}"
                    else:
                        continue
                    data = get_data_from_sscan(
                        getattr(scan, f"{category}.{item}.array"), n
                    )
                    results[signal.name] = data["value"]

            # yield all results one complete step at a time
            for i in range(n):
                yield from mkdoc(i+1, {k: results[k][i] for k in results})

        yield from read_sscan_data(self)
        self.unstage()
