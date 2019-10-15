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

# Usage:
```python
import tuyapower

PLUGID = '01234567891234567890'
PLUGIP = '10.0.1.99'
PLUGKEY = '0123456789abcdef'
PLUGVERS = '3.1'

(on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID,PLUGIP,PLUGKEY,PLUGVERS)

```
## Parameters:
* PLUGID = Device ID e.g. 01234567891234567890
* PLUGIP = Device IP Address e.g. 10.0.1.99
* PLUGKEY = Device Key e.g. 0123456789abcdef
* PLUGVERS = Version of Protocol 3.1 or 3.3
 
## Response Data: 
* on = Switch state - true or false
* w = Wattage 
* mA = milliamps 
* V = Voltage 
* err = Error message or OK

Note: If error occurs, on will be set to false, w, mA and V will be set to -99.0.
