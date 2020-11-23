# TuyaPower Module
# -*- coding: utf-8 -*-
"""
 Python module to pull power and state data from Tuya WiFi smart devices

 Author: Jason A. Cox
 For more information see https://github.com/jasonacox/tuyapower

 Functions and Usage
   (on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)
   rawData = tuyapower.deviceRaw(id, ip, key, vers)
   tuyapower.devicePrint(id, ip, key, vers)
   dataJSON = tuyapower.deviceJSON(id, ip, key, vers)
   devices = deviceScan(verbose, port)
   scan()

 Parameters Sent:
   id = Device ID e.g. 01234567891234567890
   ip = Device IP Address e.g. 10.0.1.99
   key = Device Key e.g. 0123456789abcdef
   vers = Version of Protocol 3.1 or 3.3
   verbose = True or False (print output)
   port = UDP port to scan (default 6666)

 Response Data:
   on = Switch state (single) - true or false 
   on = Switch state (multiswitch) - dictionary of state for each switch e.g. {'1':True, '2':False}
   w = Wattage (0 if error or not supported)
   mA = milliampere (0 if error or not supported)
   V = Voltage (0 if error or not supported)
   err = Error message or OK (power data found)
   rawData = Raw response from device
   devices = Dictionary of all devices found with power data if available
"""
from __future__ import print_function   # python 2.7 support
import datetime
import logging
import sys
from time import sleep
import socket
import json
from hashlib import md5
from Crypto.Cipher import AES
# Attempt to load tinytuya but fall back to pytuya if not available
try:
    import tinytuya
    api = "tinytuya"
    api_ver = tinytuya.__version__
except ImportError:
    import pytuya
    api = "pytuya"
    try:
        api_ver = pytuya.__version__
    except:
        api_ver = "unknown"

name = "tuyapower"
version_tuple = (0, 1, 0)
version = version_string = __version__ = "%d.%d.%d" % version_tuple
__author__ = "jasonacox"

log = logging.getLogger(__name__)

log.info("%s version %s", __name__, version)
log.info("Python %s on %s", sys.version, sys.platform)
log.info("Using %s version %r", api, api_ver)
    
# how my times to try to probe plug before giving up
RETRY = 5

# default polling response for error condition
_DEFAULTS = (False, 0, 0, 0)  # w, mA, V

# UDP packet payload decryption - credit to tuya-convert 
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
encrypt = lambda msg, key: AES.new(key, AES.MODE_ECB).encrypt(pad(msg).encode())
decrypt = lambda msg, key: unpad(AES.new(key, AES.MODE_ECB).decrypt(msg)).decode()
udpkey = md5(b"yGAdlopoPVldABfn").digest()
decrypt_udp = lambda msg: decrypt(msg, udpkey)

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
        V = Voltage 
        err = Error message or OK (power data found)
    """
    watchdog = 0
    now = datetime.datetime.utcnow()
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    while True:
        sw, w, mA, V = _DEFAULTS
        if(api == "tinytuya"):
            d = tinytuya.OutletDevice(deviceid, ip, key)
        else:
            d = pytuya.OutletDevice(deviceid, ip, key)
        if vers == "3.3":
            d.set_version(3.3)

        try:
            data = d.status()

        except KeyboardInterrupt:
            log.info(
                "CANCEL: Received interrupt from user while polling plug %s [%s]."
                % (deviceid, ip)
            )
            return (sw, w, mA, V, "User Interrupt")

        except:
            watchdog += 1
            if watchdog > RETRY:
                log.info(
                    "TIMEOUT: No response from plug %s [%s] after %s attempts."
                    % (deviceid, ip, RETRY)
                )
                return (sw, w, mA, V, "Timeout polling device")
            try:
                sleep(2)
                continue
            except KeyboardInterrupt:
                log.info(
                    "CANCEL: Received interrupt from user while polling plug %s [%s]."
                    % (deviceid, ip)
                )
                return (sw, w, mA, V, "User Interrupt")

        try:
            if data:
                dps = data["dps"]
                sw = dps["1"]
                # Check to see if this is a multiswitch Tuya device
                # assuming DP 2 (switch-2) and 10 (countdown-2) = multiswitch
                if "10" in dps.keys() and "2" in dps.keys():
                    # return a dictionary with all switch states
                    swDict = {}
                    for e in ["1","2","3","4","5","6","7"]:
                        if e in dps.keys():
                            swDict[e] = dps[e]
                    sw = swDict
                # Check for power data - DP 19 on some 3.1/3.3 devices
                if "19" in dps.keys():
                    w = float(dps["19"]) / 10.0
                    mA = float(dps["18"])
                    V = float(dps["20"]) / 10.0
                    key = "OK"
                # Check for power data - DP 5 for some 3.1 devices
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
                key = "Incomplete response"
            return (sw, w, mA, V, key)

        except:
            # Unable to extract data points - try again
            watchdog += 1
            if watchdog > RETRY:
                log.info(
                    "NO POWER DATA: Response from plug %s [%s] missing power data."
                    % (deviceid, ip)
                )
                return (sw, w, mA, V, "Missing Power Data")
            try:
                sleep(2)
                continue
            except KeyboardInterrupt:
                log.info(
                    "CANCEL: Received interrupt from user while polling plug %s [%s]."
                    % (deviceid, ip)
                )
                return (sw, w, mA, V, "User Interrupt")

# (dps) = tuyapower.deviceInfo(id, ip, key, vers)
def deviceRaw(deviceid, ip, key, vers):
    """Poll Device for Status - raw DPS response
       rawData = tuyapower.deviceRaw(id, ip, key, vers)

    Parameters :
        id = Device ID e.g. 01234567891234567890
        ip = Device IP Address e.g. 10.0.1.99
        key = Device Key e.g. 0123456789abcdef
        vers = Version of Protocol 3.1 or 3.3

    Response :
        rawData = Data response from device
    """
    watchdog = 0
    while True:
        data = False
        if(api == "tinytuya"):
            d = tinytuya.OutletDevice(deviceid, ip, key)
        else:
            d = pytuya.OutletDevice(deviceid, ip, key)

        if vers == "3.3":
            d.set_version(3.3)

        try:
            data = d.status()

        except KeyboardInterrupt:
            log.info(
                "CANCEL: Received interrupt from user while polling plug %s [%s]."
                % (deviceid, ip)
            )

        except:
            watchdog += 1
            if watchdog > RETRY:
                log.info(
                    "TIMEOUT: No response from plug %s [%s] after %s attempts."
                    % (deviceid, ip, RETRY)
                )
                return ("ERROR: Timeout polling device")
            try:
                sleep(2)
                continue
            except KeyboardInterrupt:
                log.info(
                    "CANCEL: Received interrupt from user while polling plug %s [%s]."
                    % (deviceid, ip)
                )

        return(data)


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
    # Poll Smart Switch for Power Data
    (on, w, mA, V, err) = deviceInfo(deviceid, ip, key, vers)

    # Check for error
    if err != "OK":
        print(" ERROR: %s\n" % err)

    # Compute projected kWh
    day = (w / 1000.0) * 24
    week = 7.0 * day
    month = (week * 52.0) / 12.0

    # Print Output 
    print("TuyaPower (Tuya Power Stats) [%s] %s [%s]"%(__version__, api, api_ver))
    print("\nDevice %s at %s key %s protocol %s:" % (deviceid,ip,key,vers))
    if isinstance(on,dict):
        print("    Switches (%d) On: %s" % (len(on),on)) 
    else:
        print("    Switch On: %r" % on)
    if err == "OK":
        print("    Power (W): %f" % w)
        print("    Current (mA): %f" % mA)
        print("    Voltage (V): %f" % V)
        print("    Projected usage (kWh):  Day: %f Week: %f  Month: %f" % (day,week,month))
    else:
        print("    NOTE: %s" % err)

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

    # Poll Smart Switch for Power Data
    (on, w, mA, V, err) = deviceInfo(deviceid, ip, key, vers)

    # Print JSON
    return (
        '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s", "response": "%s" }'
        % (iso_time, on, w, mA, V, err)
    )

# SCAN network for Tuya devices
MAXCOUNT = 15       # How many tries before stopping
DEBUG = False       # Additional details beyond verbose
UDPPORT = 6666      # Tuya 3.1 UDP Port
UDPPORTS = 6667     # Tuya 3.3 encrypted UDP Port
TIMEOUT = 3.0       # Seconds to wait for a broadcast

# Return positive number or zero
def floor(x):
    if x > 0:
            return x
    else:
            return 0

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
def scan(maxretry = MAXCOUNT):
    """Sans your network for smart plug devices with output to stdout
    """
    d = deviceScan(True,maxretry)

# Scan function
def deviceScan(verbose = False,maxretry = MAXCOUNT):
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
     # Enable UDP lisenting broadcasting mode on UDP port 6666 - 3.1 Devices
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", UDPPORT))
    client.settimeout(TIMEOUT) 
    # Enable UDP lisenting broadcasting mode on encrypted UDP port 6667 - 3.3 Devices
    clients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    clients.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    clients.bind(("", UDPPORTS))
    clients.settimeout(TIMEOUT)

    if(verbose):
        print("Scanning on UDP ports %s and %s for devices (%s retries)...\n"%(UDPPORT,UDPPORTS,maxretry))

    # globals
    devices={}
    count = 0
    counts = 0
    spinnerx = 0
    spinner = "|/-\\|"

    while (count + counts) <= maxretry:
        note = 'invalid'
        if(verbose):
            print("Scanning... %s\r"%(spinner[spinnerx]), end = '')
            spinnerx = (spinnerx + 1) % 4

        if (count <= counts):  # alternate between 6666 and 6667 ports
            try:
                data, addr = client.recvfrom(4048)
            except:
                # Timeout
                count = count + 1
                continue
        else:
            try:
                data, addr = clients.recvfrom(4048)
            except:
                # Timeout
                counts = counts + 1
                continue
        if(DEBUG): 
            print("* Message from [%s]: %s\n"%addr,data)
        ip = addr[0]
        gwId = productKey = version = ""
        result = data
        try: 
            result = data[20:-8]
            try:
                result = decrypt_udp(result)
            except:
                result = result.decode()

            result = json.loads(result)

            note = 'Valid'
            ip = result['ip']
            gwId = result['gwId']
            productKey = result['productKey']
            version = result['version']
        except:
            if(DEBUG):
                print("*  Unexpected payload=%r\n", result)
            result = {"ip": ip}
            note = "Unknown"

        # check to see if we have seen this device before and add to devices array
        if appenddevice(result, devices) == False:
            # new device found - back off count if we keep getting new devices
            if(version=='3.1'):
                count = floor(count - 1)
            else:
                counts = floor(counts - 1)
            if(verbose):
                print("FOUND Device [%s payload]: %s\n    ID = %s, product = %s, Version = %s" % (note,ip,gwId,productKey,version))
            try:
                if(version == '3.1'):
                    # Version 3.1 - no device key requires - poll for status
                    (on, w, mA, V, err) = deviceInfo(gwId, ip, productKey, version)
                    if(verbose):
                        if(err == 'OK'):
                            print("    Stats: on=%s, W=%s, mA=%s, V=%s [%s]"%(on,w,mA,V,err))
                        else:    
                            print("    Stats: on=%s [%s]"%(on,err))
                    devices[ip]['on'] = on
                    devices[ip]['w'] = w
                    devices[ip]['mA'] = mA
                    devices[ip]['V'] = V
                    devices[ip]['err'] = err
                else:
                    # Version 3.3+ requires device key
                    if(verbose):
                        print("    Device Key required to poll for stats")
            except:
                if(verbose):
                    print("    No Stats for %s: Unable to poll"%ip)
                devices[ip]['err'] = 'Unable to poll'
        else:
            if(version=='3.1'):
                count = count + 1
            else:
                counts = counts + 1

    if(verbose):
        print("                    \nScan Complete!  Found %s devices.\n"%len(devices))
        
    return(devices)
    
