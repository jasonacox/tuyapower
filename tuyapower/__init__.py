# TuyaPower Module
# Python module to pull power and state data from Tuya WiFi smart devices
#
# Author: Jason A. Cox
# For more information see https://github.com/jasonacox/powermonitor
#
# Usage:
#
# (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)
#
# Parameters Sent:
#   id = Device ID e.g. 01234567891234567890
#   ip = Device IP Address e.g. 10.0.1.99
#   key = Device Key e.g. 0123456789abcdef
#   vers = Version of Protocol 3.1 or 3.3
# 
# Response Data: 
#   on = Switch state - true or false
#   w = Wattage 
#   mA = milliamps 
#   V = Voltage (-99 if error or not supported)
#   err = Error message or OK

import pytuya
import logging
from time import sleep
import datetime
import time
import sys

name = "tuyapower"
version_tuple = (0, 0, 1)
version = version_string = __version__ = '%d.%d.%d' % version_tuple
__author__ = 'jasonacox'

log = logging.getLogger(__name__)

log.info('%s version %s', __name__, version)
log.info('Python %s on %s', sys.version, sys.platform)
log.info('Using pytuya version %r', pytuya.version)

# how my times to try to probe plug before giving up
RETRY=5

# (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)
def deviceInfo( deviceid, ip, key, vers ):
    watchdog = 0
    now = datetime.datetime.utcnow()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ") 
    while True:
        try:
            d = pytuya.OutletDevice(deviceid, ip, key)
            if vers == '3.3':
                d.set_version(3.3)

            data = d.status()
            if(d):
                sw =data['dps']['1']

                if vers == '3.3':
                    if '19' in data['dps'].keys():
                        w = (float(data['dps']['19'])/10.0)
                        mA = float(data['dps']['18'])
                        V = (float(data['dps']['20'])/10.0)
                        log.info("{ \"datetime\": \"%s\", \"switch\": \"%s\", \"power\": \"%s\", \"current\": \"%s\", \"voltage\": \"%s\" }" % (iso_time, sw, w, mA, V))
                        return sw, w, mA, V, 'OK'
                    else:
                        w = -99.0
                        mA = -99.0
                        V = -99.0
                        log.info("{ \"datetime\": \"%s\", \"switch\": \"%s\", \"power\": \"%s\", \"current\": \"%s\", \"voltage\": \"%s\" }" % (iso_time, sw, w, mA, V))
                        return sw, w, mA, V, 'Power data unavailable'
                else:
                    if '5' in data['dps'].keys():
                        w = (float(data['dps']['5'])/10.0)
                        mA = float(data['dps']['4'])
                        V = (float(data['dps']['6'])/10.0)
                        log.info("{ \"datetime\": \"%s\", \"switch\": \"%s\", \"power\": \"%s\", \"current\": \"%s\", \"voltage\": \"%s\" }" % (iso_time, sw, w, mA, V))
                        return sw, w, mA, V, 'OK'
                    else:
                        w = -99.0
                        mA = -99.0
                        V = -99.0
                        log.info("{ \"datetime\": \"%s\", \"switch\": \"%s\", \"power\": \"%s\", \"current\": \"%s\", \"voltage\": \"%s\" }" % (iso_time, sw, w, mA, V))
                        return sw, w, mA, V, 'Power data unavailable'
            else:
                log.info("Incomplete response from plug %s [%s]." % (deviceid,ip))
                sw = False
                w = -99.0
                mA = -99.0
                V = -99.0
                return sw, w, mA, V, 'Incomplete response'
            break
        except KeyboardInterrupt:
            log.info("CANCEL: Recived interrupt from user while polling plug %s [%s]." % (deviceid,ip))
            sw = False
            w = -99.0
            mA = -99.0
            V = -99.0
            return sw, w, mA, V, 'User Interrupt'
        except:
            watchdog+=1
            if(watchdog>RETRY):
                log.info("TIMEOUT: No response from plug %s [%s] after %s attempts." % (deviceid,ip,RETRY))
                sw = False
                w = -99.0
                mA = -99.0
                V = -99.0
                return sw, w, mA, V, 'Timeout polling device'
            try:
                sleep(2)
            except KeyboardInterrupt:
                log.info("CANCEL: Recived interrupt from user while polling plug %s [%s]." % (deviceid,ip))
                sw = False
                w = -99.0
                mA = -99.0
                V = -99.0
                return sw, w, mA, V, 'User Interrupt'


