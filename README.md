# TuyaPower - Python Module
This python module will poll WiFi [Tuya](https://en.tuya.com/) campatible Smart Plugs for state (on/off), current (mA), voltage (V), and power (wattage). 

# Description
This project is based on the python pytuya library to poll [Tuya](https://en.tuya.com/) campatible Smart Plugs for state and power data that can be used for point in time monitoring or stored for trending.  There are two test scripts here. The `test.py` script responds with a human redable output of state (on/off), current (mA), voltage (V), and power (W).  The `test-json.py` script responds with JSON containing the same but adds a timestamp for convient time series processing.

REQUIRED: IP address and Device ID of smart plug.

## Preparation
1. Download the Smart Life - Smart Living app for iPhone or Android. Pair with your smart plug (this is important as you cannot monitor a plug that has not been paired).  
	* https://itunes.apple.com/us/app/smart-life-smart-living/id1115101477?mt=8
	* https://play.google.com/store/apps/details?id=com.tuya.smartlife&hl=en
2. Device ID - Inside the app, select the plug you wish to monitor, select the 3 dots(Jinvoo) or the edit/pencil icon(Tuya & SmartLife) in the top right and then "Device Info".  The page should display "Device ID" which the script will use to poll the plug. It's also worth noting the MAC address of the device as it can come in handy in step 3.
3. IP Address - If your router displays a list of all the devices that are connected to it, you can search for the MAC address of the device. This is often the quickest way to locate your device IP.

	Alternatively, you will need to manually determine what IP address your network assigned to the Smart Plug - this is more difficult but it looks like `arp-scan` can help identify devices on your network.  WiFi Routers often have a list of devices connected as well. Look for devices with a name like "ESP_xxxxxx". Many modern routers allow you to set the hostname of connected devices to something more memorable, once you have located it.

4. Firmware Version - Devices with newer firmware (1.0.5 and above) are typically using a different protocol (3.3). These devices need to be communicated with using encryption and the resultant data is packaged slightly differently. It's a good idea therefore to check the Firmware version of the device(s) too. In the Tuya/SmartLife/Jinvoo app there will be a device option "Check for Firmware Upgrade" or similar. Open this option and take note of the Wi-Fi Module & MCU Module numbers. These are usually the same.  
	* Firmware 1.0.4 and lower:  DEVICEVERS = 3.1
	* Firmware 1.0.5 and above:  DEVICEVERS = 3.3 

5. Device Key - If your device is running Firmware 1.0.5 or above, you will need to obtain the Device Key. This is used to connect with the device  decrypt the power consumption data. For details on how to do this, see point 2: https://github.com/clach04/python-tuya/wiki 

## Setup: PyPi - Easy  
_Tested on RaspberryPi, Linux, and MacOS._ 
Install pip and python libraries if you haven't already:
```bash
# Install required libraries
 sudo apt-get install python-crypto python-pip		
 pip install pycrypto
 pip install pytuya
 pip install Crypto		# some systems will need this
 pip install pyaes		# some systems will need this
 pip install tuyapower  # this module

# Run a test
 $ python
 Python 2.7.13 (default, Sep 26 2018, 18:42:22) 
[GCC 6.3.0 20170516] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import tuyapower
>>> PLUGID = '01234567891234567890'
>>> PLUGIP = '10.0.0.10'
>>> PLUGKEY = '0123456789abcdef'
>>> tuyapower.deviceInfo(PLUGID,PLUGIP,PLUGKEY,'3.1')
(True, 1.2, 70.0, 121.1, 'OK')
>>> tuyapower.deviceInfo(PLUGID,PLUGIP,PLUGKEY,'3.3')
(False, -99.0, -99.0, -99.0, 'Timeout polling device')
>>> 
```

## Setup: Option 1 - Docker
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
docker run -e PLUGID='01234567891234567890' -e PLUGIP="10.0.1.x" -e PLUGKEY="0123456789abcdef" -e PLUGINVERS="3.3" tuyapower
```

## Setup: Option 2 - Manually:  
_Tested on RaspberryPi, Linux, and MacOS._ 
The script does not need docker but it does require the pytuya and pycrypto python library. Follow these steps to set it up and run the script:

1. Install pip and python libraries if you haven't already:

```bash
 sudo apt-get install python-crypto python-pip		
 pip install pycrypto
 pip install pytuya
 pip install Crypto		# some systems will need this
 pip install pyaes		# some systems will need this
 
```

2. Run the python `test.py` script:
```bash
python test.py {DEVICEID} {DEVICEIP} {DEVICEKEY [optional]} {DEVICEVERS [optional]}

#Devices with older firmware (1.0.4 and below)
$ python3 test.py 01234567891234567890 10.0.0.99
TuyaPower (Tuya Power Stats)

Device 01234567891234567890 at 10.0.0.99 key 0123456789abcdef protocal 3.1:
    Switch On: True
    Power (W): 43.100000
    Current (mA): 362.000000
    Voltage (V): 119.500000
    Projected usage (kWh):  Day: 1.034400  Week: 7.240800  Month: 31.376800

{ "datetime": "2019-10-12T21:46:50Z", "switch": "True", "power": "43.1", "current": "362.0", "voltage": "119.5" }

#Devices with newer firmware (1.0.5 and above)
$ python3 test.py 01234567891234567890 10.0.0.99 0123456789abcdef 3.3
TuyaPower (Tuya Power Stats)

Device 01234567891234567890 at 10.0.0.99 key 0123456789abcdef protocal 3.3:
    Switch On: True
    Power (W): 43.100000
    Current (mA): 362.000000
    Voltage (V): 119.500000
    Projected usage (kWh):  Day: 1.034400  Week: 7.240800  Month: 31.376800

{ "datetime": "2019-10-12T21:46:50Z", "switch": "True", "power": "43.1", "current": "362.0", "voltage": "119.5" }

```
Please note, these smart plugs and this script do not hold power usage data in memory so the "Projected usage" reported is an estimate based on current power readings and assumed steady state over time. 

## JSON Output Script
The `test-json.py` script works the same as `test.py` but produces the data in only JSON output with a datetime stamp.  This makes it easier to feed into other systems for recording, alerting or graphing.

## Example Products 
* TanTan Smart Plug Mini Wi-Fi Enabled Outlet with Energy Monitoring - https://www.amazon.com/gp/product/B075Z17987/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1
* SKYROKU SM-PW701U Wi-Fi Plug Smart Plug - see https://wikidevi.com/wiki/Xenon_SM-PW701U
* Wuudi SM-S0301-US - WIFI Smart Power Socket Multi Plug with 4 AC Outlets and 4 USB Charging
* Gosund SP1 - WiFi High Amp RatedSmart Power Socket (eu) using 3.3 Protocol - see https://www.amazon.de/Steckdose-Stromverbrauch-Funktion-Fernsteurung-Netzwerk/dp/B07B911Y6V

## Acknowledgements 
* https://github.com/clach04/python-tuya
* https://github.com/jasonacox.com/powermonitor

## Contributers
* Jason A. Cox ([jasonacox](https://github.com/jasonacox))
* Phill Healey ([codeclinic](https://github.com/codeclinic)) - Integration for firmwares (1.0.5+) / protocol v3.3 & commandline arguments.
