# TuyaPower Module
# -*- coding: utf-8 -*-
"""
 Python module to pull power and state data from Tuya WiFi smart devices

 Author: Jason A. Cox
 For more information see https://github.com/jasonacox/tuyapower

 Functions and Usage
   (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)
   tuyapower.devicePrint(id, ip, key, vers)
   dataJSON = tuyapower.deviceJSON(id, ip, key, vers)
   devices = deviceScan(verbose)
   scan()

 Parameters Sent:
   id = Device ID e.g. 01234567891234567890
   ip = Device IP Address e.g. 10.0.1.99
   key = Device Key e.g. 0123456789abcdef
   vers = Version of Protocol 3.1 or 3.3
   verbose = True or False (print output)

 Response Data:
   on = Switch state - true or false
   w = Wattage
   mA = milliamps
   V = Voltage (-99 if error or not supported)
   err = Error message or OK
   devices = Dictionary of all devices found with power data if available
"""

import datetime
import logging
import sys
from time import sleep
import socket
import json

import pytuya

name = "tuyapower"
version_tuple = (0, 0, 10)
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
    """Poll Device for State
       (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)

    Parameters :
        id = Device ID e.g. 01234567891234567890
        ip = Device IP Address e.g. 10.0.1.99
        key = Device Key e.g. 0123456789abcdef
        vers = Version of Protocol 3.1 or 3.3

    Response :
        on = Switch state - true or false
        w = Wattage
        mA = milliamps
        V = Voltage (-99 if error or not supported)
        err = Error message or OK
    """
    watchdog = 0
    now = datetime.datetime.utcnow()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    while True:
        w, mA, V = _DEFAULTS
        try:
            d = pytuya.OutletDevice(deviceid, ip, key)
            if vers == "3.3":
                d.set_version(3.3)

            data = d.status()
            if d:
                dps = data["dps"]
                sw = dps["1"]
                if vers == "3.3" and ("19" in dps.keys()):
                    w = float(dps["19"]) / 10.0
                    mA = float(dps["18"])
                    V = float(dps["20"]) / 10.0
                    key = "OK"
                elif "5" in dps.keys():
                    w = float(dps["5"]) / 10.0
                    mA = float(dps["4"])
                    V = float(dps["6"]) / 10.0
                    key = "OK"
                else:
                    key = "Power data unavailable"
                info = dict(
                    datetime=iso_time, switch=sw, power=w, current=mA, voltage=V
                )
                log.info(str(info))
            else:
                log.info("Incomplete response from plug %s [%s]." % (deviceid,ip))
                sw = False
                key = "Incomplete response"
            return (sw, w, mA, V, key)
        except KeyboardInterrupt:
            log.info(
                "CANCEL: Recived interrupt from user while polling plug %s [%s]."
                % (deviceid, ip)
            )
            sw = False
            return (sw, w, mA, V, "User Interrupt")
        except:
            watchdog += 1
            if watchdog > RETRY:
                log.info(
                    "TIMEOUT: No response from plug %s [%s] after %s attempts."
                    % (deviceid, ip, RETRY)
                )
                sw = False
                return (sw, w, mA, V, "Timeout polling device")
            try:
                sleep(2)
            except KeyboardInterrupt:
                log.info(
                    "CANCEL: Recived interrupt from user while polling plug %s [%s]."
                    % (deviceid, ip)
                )
                sw = False
                return (sw, w, mA, V, "User Interrupt")


# Print output
def devicePrint(deviceid, ip, key='0123456789abcdef', vers='3.1'):
    """Poll device and print formatted output to stdout
       tuyapower.devicePrint(id, ip, key, vers)

    Parameters :
        id = Device ID e.g. 01234567891234567890
        ip = Device IP Address e.g. 10.0.1.99
        key = Device Key e.g. 0123456789abcdef
        vers = Version of Protocol 3.1 or 3.3

    """
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
    print("\nDevice %s at %s key %s protocol %s:" % (deviceid,ip,key,vers))
    print("    Switch On: %r" % on)
    print("    Power (W): %f" % w)
    print("    Current (mA): %f" % mA)
    print("    Voltage (V): %f" % V)
    print(
        "    Projected usage (kWh):  Day: %f  Week: %f  Month: %f\n"
        % (day, week, month)
    )


# JSON response
def deviceJSON(deviceid, ip, key='0123456789abcdef', vers='3.1'):
    """Poll device on local network and return JSON formatted details
       Response = tuyapower.devicePrint(id, ip, key, vers)

    Parameters :
        id = Device ID e.g. 01234567891234567890
        ip = Device IP Address e.g. 10.0.1.99
        key = Device Key e.g. 0123456789abcdef
        vers = Version of Protocol 3.1 or 3.3

    Response:
        JSON String

    Note: Devices are only seen if within the same broadcast network segment
    """
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

# SCAN network for Tuya devices
MAXCOUNT = 10
PORT = 6666
DEBUG = False

# Store found devices in memory
def appenddevice(newdevice, devices):
    if(newdevice['ip'] in devices):
        return True
    """
    for i in devices:
        if i['ip'] == newdevice['ip']:
                return True
    """
    devices[newdevice['ip']] = newdevice
    return False

# Scan function shortcut
def scan():
    """Sans your network for smart plug devices with output to stdout
    """
    d = deviceScan(True)

# Scan function
def deviceScan(verbose = False):
    """Scans your network for smart plug devices
        devices = tuyapower.deviceScan(verbose)

    Parameters:
        verbose = True or False, print formatted output to stdout

    Response: 
        devices = Dictionary of all devices found with power data if available

        To unpack data, you can do something like this:

        devices = tuyapower.deviceScan()
        for ip in devices:
            id = devices[ip]['gwId']
            key = devices[ip]['productKey']
            vers = devices[ip]['version']
            (on, w, mA, V, err) = deviceInfo(id, ip, key, vers)
            print("Device at %s: ID %s, state=%s, W=%s, mA=%s, V=%s [%s]"%(ip,id,on,w,mA,V,err))

    """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    if(verbose):
        print("Scanning on UDP port %s for devices...\n"%PORT)
    devices={}
    count = 0
    stop = False

    client.bind(("", PORT))
    while stop == False:
        data, addr = client.recvfrom(4048)
        if(DEBUG): 
            print("* Message from [%s]: %s\n"%addr,data)
        ip = addr[0]
        gwId = productKey = version = ""
        result = data
        try: 
            result = data[20:-8]
            note = 'Valid'
            if result.startswith(b'{'):
                # this is the regular expected code path
                if not isinstance(result, str):
                    result = result.decode()
                result = json.loads(result)
            else:
                if(DEBUG):
                    print('*  Unexpected payload=%r\n', result)
                note = 'Unknown'
                result = {"ip": ip}

            ip = result['ip']
            gwId = result['gwId']
            productKey = result['productKey']
            version = result['version']
        except:
            if(DEBUG):
                print("* Bad data \n")
            result = {"ip": ip}

        if appenddevice(result, devices) == False:
            if(verbose):
                print("FOUND Device [%s payload]: %s\n    ID = %s, Key = %s, Version = %s" % (note,ip,gwId,productKey,version))
            try:
                (on, w, mA, V, err) = deviceInfo(gwId, ip, productKey, version)
                if(verbose):
                    print("    Stats: on=%s, W=%s, mA=%s, V=%s [%s]"%(on,w,mA,V,err))
                devices[ip]['on'] = on
                devices[ip]['w'] = w
                devices[ip]['mA'] = mA
                devices[ip]['V'] = V
                devices[ip]['err'] = err
            except:
                if(verbose):
                    print("    No Stats for %s: Unable to poll",ip)
                devices[ip]['err'] = 'Unable to poll'
        else:
            count = count + 1
            if count > MAXCOUNT: 
                stop = True

    if(verbose):
        print("\nScan Complete!  Found %s devices.\n"%len(devices))
        
    return(devices)
    