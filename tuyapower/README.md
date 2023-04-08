# TuyaPower - PyPi Module

[![Build Status](https://github.com/jasonacox/tuyapower/actions/workflows/test.yml/badge.svg)](https://github.com/jasonacox/tuyapower/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/tuyapower.svg)](https://badge.fury.io/py/tuyapower)

Author: Jason A. Cox 
https://github.com/jasonacox/tuyapower

# Description
Python module to pull power and state data from Tuya WiFi smart devices.  _Tested on RaspberryPi, Linux, Windows 10 and MacOS._ 

# Preparation
This module requires: pycryptodome and tinytuya (replaces pytuya).

```bash
# Install required libraries
sudo apt-get install python-crypto python-pip		# for RPi, Linux
python3 -m pip install pycryptodome    # or pycrypto, pyaes or Crypto
python3 -m pip install tinytuya        # or pytuya
python3 -m pip install tuyapower       # this tuyapower module 
```

 For Windows 10 users or if you get errors related to Crypto, try installing the pycryptodome module:
 ```bash
 pip install pycryptodome
 ```
 
# Functions
* deviceInfo - Poll device and return on, w, mA, V and err data.
    ```python
    (on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* deviceRaw - Poll device and return raw response data.
    ```python
    rawData = tuyapower.deviceRaw(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* devicePrint - Poll device and print formatted output to stdout.
    ```python
    tuyapower.devicePrint(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* deviceJSON - Poll device and return JSON formatted details.
    ```python
    dataJSON = tuyapower.deviceJSON(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* deviceScan(verbose, max_retries=15) - Scans network for smart plug devices and return dictionary of devices and power data.
    ```python
    verbose = False
    devices = tuyapower.deviceScan(verbose)
    ```
* scan(max_retries=15) - This is a shortcut for deviceScan() that prints formatted output to stdout for UDP ports 6666 and 6667. By default, the scan functions will retry 15 times to find new devices. If you are not seeing all your devices, you can increase max_retries.

## Parameters:
* PLUGID = Device ID e.g. 01234567891234567890
* PLUGIP = Device IP Address e.g. 10.0.1.99
* PLUGKEY = Device Key e.g. 0123456789abcdef
* PLUGVERS = Version of Protocol 3.1, 3.2, 3.3, 3.4 or 3.5
* verbose = Print more details - True or False (default is False)
* max_retries = Number of times to retry scan of new devices (default is 15)
 
## Response Data: 
* on = Switch state - true or false
* w = Wattage 
* mA = milliamps 
* V = Voltage 
* err = Error message or OK
* rawData = Raw response from device
* devices = Dictionary of all devices found with power data if available

Note: If error occurs, on will be set to false, w, mA and V will be set to -99.0.

# Example Usage:
```python

# Poll a Single Devices
import tuyapower

PLUGID = '01234567891234567890'
PLUGIP = '10.0.1.99'
PLUGKEY = '0123456789abcdef'
PLUGVERS = '3.1'

(on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID,PLUGIP,PLUGKEY,PLUGVERS)

# Scan Network for All Devices
# To see output on stdout set verbose True
tuyapower.deviceScan(True)
Scanning on UDP port 6666 for devices...

FOUND Device [Valid payload]: 10.0.1.100
    ID = 01234567891234567890, Key = 0123456789abcdef, Version = 3.1
    Stats: on=True, W=6.0, mA=54.0, V=121.1 [OK]
FOUND Device [Valid payload]: 10.0.1.200
    ID = 01234567891234567891, Key = 0123456789abcdea, Version = 3.1
    Stats: on=True, W=-99, mA=-99, V=-99 [Power data unavailable]

Scan Complete!  Found 2 devices.

# Scan the network and unpack the response 
devices = tuyapower.deviceScan()
    for ip in devices:
        id = devices[ip]['gwId']
        key = devices[ip]['productKey']
        vers = devices[ip]['version']
        (on, w, mA, V, err) = deviceInfo(id, ip, key, vers)
        print("Device at %s: ID %s, state=%s, W=%s, mA=%s, V=%s [%s]"%(ip,id,on,w,mA,V,err))
```

### Scan Tool 
The function `tuyapower.scan()` will listen to your local network (UDP 6666 and 6667) and identify Tuya devices broadcasting their IP, Device ID, productKey and Version and will print that and their stats to stdout.  This can help you get a list of compatible devices on your network. The `tuyapower.deviceScan()` function returns all found devices and their stats (via dictionary result).

You can run the scanner from the command line using this:
```bash
python -m tuyapower
```

By default, the scan functions will retry 15 times to find new devices. If you are not seeing all your devices, you can increase max_retries by passing an optional arguments (ex. 50 retries):

```bash
# command line
python -m tuyapower 50
```

```python
# invoke verbose interactive scan
tuyapower.scan(50)

# return payload of devices
devices = tuyapower.deviceScan(false, 50)
```