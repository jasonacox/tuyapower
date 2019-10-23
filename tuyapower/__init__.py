# TuyaPower Module
# Python module to pull power and state data from Tuya WiFi smart devices
#
# Author: Jason A. Cox
# For more information see https://github.com/jasonacox/powermonitor
#
# Functions and Usage
#   (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)
#   tuyapower.devicePrint(id, ip, key, vers)
#   dataJSON = tuyapower.deviceJSON(id, ip, key, vers)
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

import collections
import datetime
import logging
import sys
import time
from time import sleep

import pytuya

name = "tuyapower"
version_tuple = (0, 0, 7)
version = version_string = __version__ = "%d.%d.%d" % version_tuple
__author__ = "jasonacox"

log = logging.getLogger(__name__)

log.info("%s version %s", __name__, version)
log.info("Python %s on %s", sys.version, sys.platform)
log.info("Using pytuya version %r", pytuya.version)

# how my times to try to probe plug before giving up
RETRY = 5

_DEFAULTS = (-99, -99, -99)  # w, mA, V

# (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)
def deviceInfo(deviceid, ip, key, vers):
    watchdog = 0
    now = datetime.datetime.utcnow()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    while True:
        try:
            d = pytuya.OutletDevice(deviceid, ip, key)
            if vers == "3.3":
                d.set_version(3.3)

            data = d.status()
            if d:
                dps = data["dps"]
                sw = dps["1"]

                if vers == "3.3":
                    if "19" in dps.keys():
                        w = float(dps["19"]) / 10.0
                        mA = float(dps["18"])
                        V = float(dps["20"]) / 10.0
                        log.info(
                            '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s" }'
                            % (iso_time, sw, w, mA, V)
                        )
                        return sw, w, mA, V, "OK"
                    else:
                        w, mA, V = _DEFAULTS
                        log.info(
                            '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s" }'
                            % (iso_time, sw, w, mA, V)
                        )
                        return (sw, w, mA, V, "Power data unavailable")
                else:
                    if "5" in dps.keys():
                        w = float(dps["5"]) / 10.0
                        mA = float(dps["4"])
                        V = float(dps["6"]) / 10.0
                        log.info(
                            '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s" }'
                            % (iso_time, sw, w, mA, V)
                        )
                        return (sw, w, mA, V, "OK")
                    else:
                        w, mA, V = _DEFAULTS
                        log.info(
                            '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s" }'
                            % (iso_time, sw, w, mA, V)
                        )
                        return (sw, w, mA, V, "Power data unavailable")
            else:
                log.info(f"Incomplete response from plug {deviceid} [{ip}].")
                sw = False
                w, mA, V = _DEFAULTS
                return (sw, w, mA, V, "Incomplete response")
            break
        except KeyboardInterrupt:
            log.info(
                "CANCEL: Recived interrupt from user while polling plug %s [%s]."
                % (deviceid, ip)
            )
            sw = False
            w, mA, V = _DEFAULTS
            return (sw, w, mA, V, "User Interrupt")
        except:
            watchdog += 1
            if watchdog > RETRY:
                log.info(
                    "TIMEOUT: No response from plug %s [%s] after %s attempts."
                    % (deviceid, ip, RETRY)
                )
                sw = False
                w, mA, V = _DEFAULTS
                return (sw, w, mA, V, "Timeout polling device")
            try:
                sleep(2)
            except KeyboardInterrupt:
                log.info(
                    "CANCEL: Recived interrupt from user while polling plug %s [%s]."
                    % (deviceid, ip)
                )
                sw = False
                w, mA, V = _DEFAULTS
                return (sw, w, mA, V, "User Interrupt")


# Print output
def devicePrint(deviceid, ip, key, vers):
    # grab timestamp
    now = datetime.datetime.utcnow()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Poll Smart Swich for Power Data
    (on, w, mA, V, err) = deviceInfo(deviceid, ip, key, vers)

    # Check for error
    if err != "OK":
        print(" ERROR: %s\n" % err)

    # Compute projected kWh
    day = (w / 1000.0) * 24
    week = 7.0 * day
    month = (week * 52.0) / 12.0

    # Print Output
    print("TuyaPower (Tuya Power Stats)")
    print(f"\nDevice {deviceid} at {ip} key {key} protocol {vers}:")
    print("    Switch On: %r" % on)
    print("    Power (W): %f" % w)
    print("    Current (mA): %f" % mA)
    print("    Voltage (V): %f" % V)
    print(
        "    Projected usage (kWh):  Day: %f  Week: %f  Month: %f\n"
        % (day, week, month)
    )


# JSON response
def deviceJSON(deviceid, ip, key, vers):
    # grab timestamp
    now = datetime.datetime.utcnow()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Poll Smart Swich for Power Data
    (on, w, mA, V, err) = deviceInfo(deviceid, ip, key, vers)

    # Print JSON
    return (
        '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s", "response": "%s" }'
        % (iso_time, on, w, mA, V, err)
    )
