#!/usr/bin/python
#
# TuyaPower (Tuya Power Stats)
#      Power Probe - Wattage of smartplugs - JSON Output

import datetime
import os
import sys
import time
from time import sleep

import tuyapower

# Read command line options or set defaults
if (len(sys.argv) < 2) and not (("PLUGID" in os.environ) or ("PLUGIP" in os.environ)):
    print("TuyaPower (Tuya Power Stats) [%s] %s [%s]"%(tuyapower.__version__,tuyapower.api,tuyapower.api_ver))
    print("Usage: %s <PLUGID> <PLUGIP> <PLUGKEY> <PLUGVERS>\n" % sys.argv[0])
    print("    Required: <PLUGID> is the Device ID e.g. 01234567891234567890")
    print("              <PLUGIP> is the IP address of the smart plug e.g. 10.0.1.99")
    print("    Optional: <PLUGKEY> is the Device Key (default 0123456789abcdef)")
    print("              <PLUGVERS> is the Firmware Version 3.1 (default), 3.2, 3.3, 3.4 or 3.5\n")
    print("    Note: You may also send values via Environmental variables: ")
    print("              PLUGID, PLUGIP, PLUGKEY, PLUGVERS\n")
    exit()
DEVICEID = sys.argv[1] if len(sys.argv) >= 2 else "01234567891234567890"
DEVICEIP = sys.argv[2] if len(sys.argv) >= 3 else "10.0.1.99"
DEVICEKEY = sys.argv[3] if len(sys.argv) >= 4 else "0123456789abcdef"
DEVICEVERS = sys.argv[4] if len(sys.argv) >= 5 else "3.1"

# Check for environmental variables and always use those if available (required for Docker)
PLUGID = os.getenv("PLUGID", DEVICEID)
PLUGIP = os.getenv("PLUGIP", DEVICEIP)
PLUGKEY = os.getenv("PLUGKEY", DEVICEKEY)
PLUGVERS = os.getenv("PLUGVERS", DEVICEVERS)

now = datetime.datetime.utcnow()
iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

# Poll Smart Swich for Power Data
(on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)

# Print output json
responsejson = (
    '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s", "error": "%s" }'
    % (iso_time, on, w, mA, V, err)
)
print(responsejson)
