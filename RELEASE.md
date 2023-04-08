# RELEASE NOTES

## v0.2.0 - New Tuya Device Support

* PyPI 0.2.0
* Add support for Tuya protocols 3.2, 3.4 and 3.5 devices

## v0.1.0

* PyPI 0.1.0
* Added support for multi-switch devices
* Update to use tinytuya in Docker by @stevoh6 in #16
* Added err variable to output by @gamuama in #23

## v0.0.25

* Bug fix in deviceRaw() not honoring timeout settings
* Set sw response variable to False as default

## v0.0.24

* deviceInfo() - Added better error handling for devices without expect outlet/power data in their dps response.
* deviceRaw() - Added new function to return raw device data response.
* test.py & plugpower.py - Updated to add device raw data to output.

## v0.0.23 - TinyTuya

* Added support to use tinytuya, replacing pytuya:
* dds support for Device IDs that are 22 characters long (pytuya only supports 20)
* Removed misleading productKey (product SKU identity, not local Key) from scan() output
* Attempts to import tinytuya but falls back to pytuya if unavailable

## v0.0.22 - Scan Max Retry Option

* Added option to allow users to specify maximum retries for scan functions:

```bash
# specify 50 retries via command line
python3 -m tuyapower 50
```

```python
# invoke verbose interactive scan
tuyapower.scan(50)

# return payload of devices
devices = tuyapower.deviceScan(false, 50)
```

