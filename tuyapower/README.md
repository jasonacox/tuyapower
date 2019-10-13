# TuyaPower - PyPi Module
Author: Jason A. Cox 
https://github.com/jasonacox/tuyapower

# Description
Python module to pull power and state data from Tuya WiFi smart devices.

# Preparation
```bash
 sudo apt-get install python-crypto python-pip		
 pip install pycrypto
 pip install pytuya
 pip install Crypto		# some systems will need this
 pip install pyaes		# some systems will need this
```
# Functions
* deviceInfo - Poll device and return on, w, mA, V and err data.
   `(on, w, mA, V, err) = tuyapower.deviceInfo(id, ip, key, vers)`
* devicePrint - Poll device and print formatted output to stdout.
   `tuyapower.devicePrint(id, ip, key, vers)`
* deviceJSON - Poll device and return JSON formatted details.
   `dataJSON = tuyapower.deviceJSON(id, ip, key, vers)`

# Usage:
```python
import tuyapower

PLUGID = '01234567891234567890'
PLUGIP = '10.0.1.99'
PLUGKEY = '0123456789abcdef'
DEVICEVERS = '3.1'

(on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID,PLUGIP,PLUGKEY,PLUGVERS)

```
## Parameters:
* id = Device ID e.g. 01234567891234567890
* ip = Device IP Address e.g. 10.0.1.99
* key = Device Key e.g. 0123456789abcdef
* vers = Version of Protocol 3.1 or 3.3
 
## Response Data: 
* on = Switch state - true or false
* w = Wattage 
* mA = milliamps 
* V = Voltage 
* err = Error message or OK

Note: If error occurs, on will be set to false, w, mA and V will be set to -99.0.
