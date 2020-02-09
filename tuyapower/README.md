# TuyaPower - PyPi Module
Author: Jason A. Cox 
https://github.com/jasonacox/tuyapower

# Description
Python module to pull power and state data from Tuya WiFi smart devices.  _Tested on RaspberryPi, Linux, Windows 10 and MacOS._ 

# Preparation
This module requires: pycrypto, pytuya, Crypto and pyaes.

```bash
 sudo apt-get install python-crypto python-pip		
 pip install pycrypto
 pip install pytuya
 pip install Crypto		
 pip install pyaes		
```
# Functions
* deviceInfo - Poll device and return on, w, mA, V and err data.
    ```python
    (on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* devicePrint - Poll device and print formatted output to stdout.
    ```python
    tuyapower.devicePrint(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* deviceJSON - Poll device and return JSON formatted details.
    ```python
    dataJSON = tuyapower.deviceJSON(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
    ```
* deviceScan(verbose) - Scans network for smart plug devices and return dictionary of devices and power data.
    ```python
    verbose = False
    devices = tuyapower.deviceScan(verbose)
    ```
* scan() - This is a shortcut for deviceScan() that prints formatted output to stdout for UDP ports 6666 and 6667

## Parameters:
* PLUGID = Device ID e.g. 01234567891234567890
* PLUGIP = Device IP Address e.g. 10.0.1.99
* PLUGKEY = Device Key e.g. 0123456789abcdef
* PLUGVERS = Version of Protocol 3.1 or 3.3
* verbose = Print more details - True or False (default is False)
 
## Response Data: 
* on = Switch state - true or false
* w = Wattage 
* mA = milliamps 
* V = Voltage 
* err = Error message or OK
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