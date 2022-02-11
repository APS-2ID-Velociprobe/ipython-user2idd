"""
Velociprobe fly scanning device loader

M. Wyman 2022-02-11
"""

""" Loads a new flyer device """

from ..devices.ad_eiger import LocalEigerDetector
from ..devices.flyers import PmacEigerFlyer
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_eiger']

pmac_base_pv = '2iddTAU:pmac1:'
monitor_pv = '2iddf:9440:1:bi_1.VAL'
eiger_base_pv = 'dp_eiger_xrd2:'


def load_flyer(pmac_pv = pmac_base_pv, acro_pv = monitor_pv, 
               eiger_pv = eiger_base_pv, name = 'vpFlyer'):

    print('Using PMAC at : ',pmac_pv)
    print('Using PMAC monitor : ', acro_pv)
    print('Using Eiger at : ', eiger_pv)

    peFlyer = PmacEigerFlyer(pmac_pv, acro_pv, eiger_pv, acro_pv, name = 'vpFlyer')

    return peFlyer
