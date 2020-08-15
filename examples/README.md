# Examples

This contains examples scripts for using `tuyapower`.

## Example.py

This example script reads a JSON file (devices.json) to get name, device ID and device key
for a set of smart devices to poll.  It will use the tuyapower network scanning function to discover
the IP address for these devices.  It will then loop through each device and display state (on/off) 
and any power data that may be available (for devices that monitor power).

The devices.json file can be created from the output of the "tuya-cli wizard" command to 
gather ID and Keys for all devices registered on your network. Information on how to do this is in
the tuyapower [README](../README.md). You can also watch this great 'Tech With Eddie YouTube tutorial
that will walk you through getting your Tuya device keys: https://youtu.be/oq0JL_wicKg 

Note: the output of the "tuya-cli wizard" command is improperly formatted JSON. I'm using the
demjson module to read the dirty JSON so that you can simply copy and paste the output from the
"tuya-cli wizard" command into the devices.json file. 

```
python3 example.py

Loading Tuya Keys...
    3 device keys loaded

Scanning network for Tuya devices...
    14 devices found

Polling devices...
    [Smart Plug] - Off - Power: 0.0W, 0.0mA, 118.6V
    [Fan] - On
    [Fridge] - On - Power: 53.4W, 475.0mA, 120.1V
```
