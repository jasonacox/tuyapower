# TuyaPower - Python Module
This python module will poll WiFi [Tuya](https://en.tuya.com/) campatible Smart Plugs for state (on/off), current (mA), voltage (V), and power (wattage). 

# Description
This project is based on the python pytuya library to poll [Tuya](https://en.tuya.com/) campatible Smart Plugs for state and power data that can be used for point in time monitoring or stored for trending.  There are two test scripts here. The `test.py` script responds with a human redable output of state (on/off), current (mA), voltage (V), and power (W).  The `test-json.py` script responds with JSON containing the same but adds a timestamp for convient time series processing.

## Preparation
The tuyapower module includes a scanner function `deviceScan()` to find Smart Plugs on your network.  However, it may or may not be able to detect all of them. You can use the following to manually identify the required IP address and Device ID of the smart plug:

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

## Setup  
_Tested on RaspberryPi, Linux, Windows 10 and MacOS._ 
Install pip and python libraries if you haven't already:
```bash
# Install required libraries
 sudo apt-get install python-crypto python-pip		# for RPi, Linux
 pip install pycryptodome  # or pycrypto or Crypto
 pip install pyaes
 pip install pytuya
 pip install tuyapower  # Pull this tuyapower module from PyPi
 ```
 
### Scan Tool 
The function `tuyapower.scan()` will listen to your local network and identify Tuya devices broadcasting their IP, Device ID, Key and Version and will print that and their stats to stdout.  This can help you get a list of compatible devices on your network. The `tuyapower.deviceScan()` function returns all found devices and their stats (via dictionary result).

You can run the scanner from the command line using this:
```bash
python -m tuyapower
```

 ## Exmaple Usage
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

## Setup: Optional - Docker
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

Please note, these smart plugs and this script do not hold power usage data in memory so the "Projected usage" reported is an estimate based on current power readings and assumed steady state over time. 

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
