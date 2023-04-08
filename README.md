# TuyaPower - Python Module

[![Build Status](https://github.com/jasonacox/tuyapower/actions/workflows/test.yml/badge.svg)](https://github.com/jasonacox/tuyapower/actions/workflows/test.yml)
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

Pulling data from Tuya devices on your network requires that you have the Device *IP*, *ID*, *VERSION* and *KEY* (for 3.3 devices). The `tuyapower` and `tinytuya` modules include a scanner function to find Smart Plugs on your network.  This will scan the network and identify Device's *IP*, *ID* and *VERSION*.  It will not be able to get the local *KEY*.  Since newer 3.3 devices will require the *KEY*, the following steps will help you determine the *KEY*s for your devices:

### Get the Tuya Device KEY

1. Download the "Smart Life" - Smart Living app for iPhone or Android. Pair with your smart plug (this is important as you cannot monitor a plug that has not been paired).  
    * https://itunes.apple.com/us/app/smart-life-smart-living/id1115101477?mt=8
    * https://play.google.com/store/apps/details?id=com.tuya.smartlife&hl=en
2. For Device IP, ID and VERSION: Run the tuyapower scan to get a list of Tuya devices on your network along with their device IP, ID and VERSION number (3.1 to 3.5 - most are 3.3):
    ```bash
    python3 -m tuyapower
    ```
3. For Device KEY: If your device is running the latest protocol version 3.3 (often seen with Firmware 1.0.5 or above), you will need to obtain the Device Key. This is used to connect with the device and decrypt the response data. The following are instructions to do this and are based on <https://github.com/codetheweb/tuyapi/blob/master/docs/SETUP.md>:

  * **From iot.tuya.com**
    * Create a Tuya Developer account on [iot.tuya.com](https://iot.tuya.com/) and log in.
    * Click on "Cloud" icon -> Create a project (remember the Authorization Key: *API ID* and *Secret* for below)
    * Click on "Cloud" icon -> select your project -> Project Overview -> Linked Device -> Link devices by App Account (tab)
    * Click 'Add App Account' and it will display a QR code. Scan the QR code with the *Smart Life app* on your Phone (see step 1 above) by going to the "Me" tab in the *Smart Life app* and clicking on the QR code button [..] in the upper right hand corner of the app. When you scan the QR code, it will link all of the devices registered in your "Smart Life" app into your Tuya IoT project.
    * **IMPORTANT** Under "API Management" -> "API Products" and ensure the API groups have status "Subscribed": Smart Home Devices Management, Authorization and Smart Home Family Management ([see screenshot here](https://user-images.githubusercontent.com/836718/111419675-1d0d3f80-86a7-11eb-81ad-f6078ee391fe.png)) - Make sure you authorize your Project to use these 3 API groups:
        - Click each of the API boxes
        - Click "Projects" tab
        - Click "**New Authorization**" button
        - Select your Project from the dropdown and click OK ([see screenshot here](https://user-images.githubusercontent.com/836718/111578175-d5eb8100-8770-11eb-93b3-46342b1a67fa.png))

  * **From your Local Workstation**
    * From your PC/Mac you can run the TinyTuya Setup **Wizard** to fetch the Device KEYs for all of your
    registered devices:
    ```
    python3 -m tinytuya wizard

    # If you are using windows command prompt w/o color use:
    python -m tinytuya wizard -nocolor
    ```
    * The **Wizard** will prompt you for the *API ID* key, API *Secret*, API *Region* (us, eu, cn or in) from your Tuya IoT project noted above.  It will also ask for a sample *Device ID*.  Use one from step 2 above or found in the Device List on your Tuya IoT project.
    * The **Wizard** will poll the Tuya IoT Platform and print a JSON list of all your registered devices with the "name", "id" and "key" of your registered device(s). The "key"s in this list are the Device *KEYs* you will use to poll your devices.
    * In addition to displaying the list of devices, **Wizard** will create a local file `devices.json`.  TinyTuya will use this file to provide additional details to scan results from `tinytuya.scanDevices()` or when running `python3 -m tinytuya` to scan your local network.

Notes:
* If you ever reset or re-pair your smart devices, they will reset their *LOCAL_KEY* and you will need to repeat these steps above. 
* The TinyTuya *Wizard* was inspired by the TuyAPI CLI which is an alternative way to fetch the *Device KEYs*: `npm i @tuyapi/cli -g` and run `tuya-cli wizard`
* For a helpful video walk-through of getting the KEYS you can also watch this great _Tech With Eddie_ YouTube tutorial: <https://youtu.be/oq0JL_wicKg>.

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
* PLUGVERS = Version of Protocol 3.1, 3.2, 3.3, 3.4 or 3.5
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

## Docker Usage (Optional)

![Docker Pulls](https://img.shields.io/docker/pulls/jasonacox/tuyapower)

A docker container version of the tuyapower library is available on DockerHub and can be used to grab power data without installing the python libraries.

```bash
# Friendly Output
# Run tuyapower container - replace with device ID, IP and VERS
docker run -e PLUGID="01234567891234567890" \
    -e PLUGIP="10.0.1.x" \
    -e PLUGKEY="0123456789abcdef" \
    -e PLUGVERS="3.3" \
    jasonacox/tuyapower

# JSON Output
# Run tuyapower container - replace with device ID, IP and VERS
docker run -e PLUGID="01234567891234567890" \
    -e PLUGIP="10.0.1.x" \
    -e PLUGKEY="0123456789abcdef" \
    -e PLUGVERS="3.3" \
    -e PLUGJSON="yes" \
    jasonacox/tuyapower
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
