# TuyaPower - Python Module

[![Build Status](https://travis-ci.org/jasonacox/tuyapower.svg?branch=master)](https://travis-ci.org/jasonacox/tuyapower)
[![PyPI version](https://badge.fury.io/py/tuyapower.svg)](https://badge.fury.io/py/tuyapower)

This python module will poll WiFi [Tuya](https://en.tuya.com/) compatible Smart Plugs/Switches/Lights for state (on/off), current (mA), voltage (V), and power (wattage).

## Description

This module uses the python [tinytuya](https://github.com/jasonacox/tinytuya) or pytuya library to poll [Tuya](https://en.tuya.com/) compatible Smart Plugs, Switches and Lights for state and power data that can be used for point in time monitoring or stored for trending.  There are two test scripts here. The [plugpower.py](plugpower.py) script responds with a human readable output of state (on/off), current (mA), voltage (V), and power (W).  The [plugjson.py](plugjson.py) script responds with JSON containing the same but adds a timestamp for convenient time series processing.

## TuyaPower Setup  

_Tested on RaspberryPi, Linux, Windows 10 and MacOS._ 
Install pip and the following python libraries if you haven't already. 

TuyaPower has been updated to use `tinytuya`, a fork of `pytuya` that adds support for device IDs of 20 and 22 characters (pytuya only supports 20 character IDs).  Install `tinytuya` to take advantage of that feature.

```bash
# Install required libraries
 sudo apt-get install python-crypto python-pip  # for RPi, Linux
 python3 -m pip install pycryptodome            # or pycrypto, pyaes, Crypto
 python3 -m pip install tinytuya                # or pytuya
 python3 -m pip install tuyapower               # Pull this tuyapower module from PyPi
 ```

## Tuya Device Preparation

Pulling data from Tuya devices on your network requires that you have the Device *IP*, *ID*, *VERSION* and *KEY* (for 3.3 devices). The `tuyapower` module includes a scanner function to find Smart Plugs on your network.  This will scan the network and identify Device's *IP*, *ID* and *VERSION*.  It will not be able to get the local *KEY*.  Since newer 3.3 devices will require the *KEY*, the following steps will help you determine the *KEY*s for your devices:

### Get the Tuya Device KEY

1. Download the "Smart Life" - Smart Living app for iPhone or Android. Pair with your smart plug (this is important as you cannot monitor a plug that has not been paired).  
    * https://itunes.apple.com/us/app/smart-life-smart-living/id1115101477?mt=8
    * https://play.google.com/store/apps/details?id=com.tuya.smartlife&hl=en
2. For Device IP, ID and VERSION: Run the tuyapower scan to get a list of Tuya devices on your network along with their device IP, ID and VERSION number (3.1 or 3.3):
    ```bash
    python3 -m tuyapower
    ```
3. For Device KEY: If your device is running the latest protocol version 3.3 (often seen with Firmware 1.0.5 or above), you will need to obtain the Device Key. This is used to connect with the device and decrypt the response data. The following are instructions to do this and are based on <https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md>:

    * **From iot.tuya.com**
    * Create a Tuya developer account on [iot.tuya.com](https://iot.tuya.com/) and log in.
    * Go to Cloud Development -> Create a project  (note the Authorization Key: *ID* & *Secret* for below)
    * Go to Cloud Development -> select your project -> Project Overview -> Linked Device -> Link devices by App Account (tab)
    * Click 'Add App Account' and it will display a QR code. Scan the QR code with the *Smart Life app* on your Phone (see step 1 above) by going to the "Me" tab in the *Smart Life app* and clicking on the QR code button [..] in the upper right hand corner of the app. When you scan the QR code, it will link all of the devices registered in your *Smart Life app* into your Tuya IoT project.
    * Verify under Cloud Development -> select your project -> API Setting that the following API groups have status "Open": Authorization management, Device Management and Device Control ([see here](https://user-images.githubusercontent.com/5875512/92361673-15864000-f132-11ea-9a01-9c715116456f.png))
    * **From your Local Workstation**
    * From your PC/Mac run this to install the Tuya CLI: `npm i @tuyapi/cli -g`
    * Next run: `tuya-cli wizard` and it will prompt you for the API *ID* key and *Secret* from your Tuya IoT project we noted above.  The Virtual ID is the Device ID from step 2 above or in the Device List on your Tuya IoT project.
    * The wizard will take a while but eventually print a JSON looking output that contains the name, id and key of the registered device(s).  This is the KEY (PLUGKEY) you will use to poll your device.

Note: If you reset or re-pair your smart devices, they will reset their local KEY and you will need to repeat these steps above.

For a helpful video walk-through of getting the KEYS you can also watch this great _Tech With Eddie_ YouTube tutorial: <https://youtu.be/oq0JL_wicKg>.

## Programming with TuyaPower

### TuyaPower Module Functions

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

### Parameters:

* PLUGID = Device ID e.g. 01234567891234567890
* PLUGIP = Device IP Address e.g. 10.0.1.99
* PLUGKEY = Device Key e.g. 0123456789abcdef
* PLUGVERS = Version of Protocol 3.1 or 3.3
* verbose = Print more details - True or False (default is False)
* max_retries = Number of times to retry scan of new devices (default is 15)

### Response Data:

* on = Switch state (single) - true or false 
* on = Switch state (multiswitch) - dictionary of state for each switch e.g. {'1':True, '2':False}
* w = Wattage 
* mA = milliamps 
* V = Voltage 
* err = Error message or OK (power data found)
* rawData = Raw response from device
* devices = Dictionary of all devices found with power data if available

Note: If error occurs, on will be set to false, w, mA and V will be set to 0.

### Programming Examples

You can import the tuyapower module into your own python projects and use the deviceInfo(), deviceJSON(), deviceScan() and devicePrint() functions to access data on your Tuya devices.  Here are some examples:

 ``` python
# Poll a Single Devices
import tuyapower

PLUGID = '01234567891234567890'
PLUGIP = '10.0.1.99'
PLUGKEY = '0123456789abcdef'
PLUGVERS = '3.1'

(on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID,PLUGIP,PLUGKEY,PLUGVERS)

tuyapower.deviceJSON(PLUGID,PLUGIP,PLUGKEY,PLUGVERS)
'{ "datetime": "2019-10-13T03:58:57Z", "switch": "True", "power": "1.2", "current": "70.0", "voltage": "122.1", "response": "OK" }'

tuyapower.devicePrint(PLUGID,PLUGIP,PLUGKEY,PLUGVERS)
TuyaPower (Tuya Power Stats)

Device 03200160dc4f2216ff61 at 10.0.1.5 key 0123456789abcdef protocol 3.1:
    Switch On: True
    Power (W): 1.200000
    Current (mA): 70.000000
    Voltage (V): 122.100000
    Projected usage (kWh):  Day: 0.028800  Week: 0.201600  Month: 0.873600

# Scan Network for All Devices
# To see output on stdout set verbose True
tuyapower.deviceScan(True)
TuyaPower (Tuya compatible smart plug scanner) [0.0.16]

Scanning on UDP ports 6666 and 6667 for devices...

FOUND Device [Valid payload]: 10.0.1.100
    ID = 01234567891234567890, Key = 0123456789abcdef, Version = 3.1
    Stats: on=True, W=6.0, mA=54.0, V=121.1 [OK]
FOUND Device [Valid payload]: 10.0.1.200
    ID = 01234567891234567891, Key = 0123456789abcdea, Version = 3.1
    Stats: on=True, W=-99, mA=-99, V=-99 [Power data unavailable]
FOUND Device [Valid payload]: 10.0.1.222
    ID = 01234567891234567893, productKey = 0123456789abcdea, Version = 3.3
    Device Key required to poll for stats

Scan Complete!  Found 3 devices.

# Scan the network and unpack the response 
devices = tuyapower.deviceScan()
    for ip in devices:
        id = devices[ip]['gwId']
        key = devices[ip]['productKey']
        vers = devices[ip]['version']
        (on, w, mA, V, err) = deviceInfo(id, ip, key, vers)
        print("Device at %s: ID %s, state=%s, W=%s, mA=%s, V=%s [%s]"%(ip,id,on,w,mA,V,err))
```

## Tuya Device Scan Tool

The function `tuyapower.scan()` will listen to your local network and identify Tuya devices broadcasting their IP, Device ID, Product Key (not the Local KEY) and protocol Version.  It will print the list of devices and for 3.1 protocol devices that don't require local KEY, it will display their energy stats.  This can help you get a list of compatible devices on your network. The `tuyapower.deviceScan()` function returns all found devices and their stats via a dictionary result.

You can run the scanner from the command line using this:

```bash
python3 -m tuyapower
```

By default, the scan functions will retry 15 times to find new devices. If you are not seeing all your devices, you can increase max_retries by passing an optional arguments (ex. 50 retries):

```bash
# command line
python3 -m tuyapower 50
```

```python
# invoke verbose interactive scan
tuyapower.scan(50)

# return payload of devices
devices = tuyapower.deviceScan(false, 50)
```

## Docker Setup (Optional)

_Tested on Linux and MacOS._
Build a docker container using `Dockerfile`
```bash
# build tuyapower container
docker build -t tuyapower .

# Devices with older firmware (1.0.4 and below)
# run tuyapower container - replace with device ID and IP 
docker run -e PLUGID='01234567891234567890' -e PLUGIP="10.0.1.x" -e PLUGKEY="0123456789abcdef" tuyapower

# Devices with newer firmware (1.0.5 and above)
# run tuyapower container - replace with device ID and IP 
docker run -e PLUGID='01234567891234567890' -e PLUGIP="10.0.1.x" -e PLUGKEY="0123456789abcdef" -e PLUGVERS="3.3" tuyapower
```

## Example Products

* TanTan Smart Plug Mini Wi-Fi Enabled Outlet with Energy Monitoring (3.1 protocol device) - https://www.amazon.com/gp/product/B075Z17987/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1
* SKYROKU SM-PW701U Wi-Fi Plug Smart Plug - https://wikidevi.com/wiki/Xenon_SM-PW701U
* Wuudi SM-S0301-US - WIFI Smart Power Socket Multi Plug with 4 AC Outlets and 4 USB Charging
* Gosund SP1 - WiFi High Amp RatedSmart Power Socket (eu) (3.3 protocol device) - https://www.amazon.de/Steckdose-Stromverbrauch-Funktion-Fernsteurung-Netzwerk/dp/B07B911Y6V
* Gosund - Smart Light Switch (us) (3.3 protocol device) - https://www.amazon.com/gp/product/B07DQG4K52/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1 
* GoKlug - Smart Plug with Energy Monitoring (us) (3.3 protocol device) - https://www.amazon.com/gp/product/B083SK787X/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1
* Treatlife WiFi Light Switch 3 Way Switch (us) (3.3 protocol device) - https://www.amazon.com/gp/product/B07V4X7BRT/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1

## Acknowledgements

  * TuyaAPI https://github.com/codetheweb/tuyapi by codetheweb and blackrozes
    For protocol reverse engineering, additional protocol reverse engineering from jepsonrob and clach04
  * PyTuya https://github.com/clach04/python-tuya by clach04
    The origin of this python module (now abandoned)
  * https://github.com/rospogrigio/localtuya-homeassistant by rospogrigio
    Edit to pytuya to support devices with Device IDs of 22 characters
  * PowerMonitor https://github.com/jasonacox/powermonitor


## Contributors

* Jason A. Cox ([jasonacox](https://github.com/jasonacox))
* Phill Healey ([codeclinic](https://github.com/codeclinic)) - Integration for firmware 1.0.5+ / protocol v3.3 & commandline arguments.
