#!/usr/bin/python
#
# TuyaPower (Tuya Power Stats)
#      Power Probe - Wattage of smartplugs

import datetime
import os
import sys

import tuyapower

# Read command line options or set defaults
if (len(sys.argv) < 2) and not (("PLUGID" in os.environ) or ("PLUGIP" in os.environ)):
    print("TuyaPower (Tuya Power Stats) [%s] %s [%s]"%(tuyapower.__version__,tuyapower.api,tuyapower.api_ver))
    print("")
    print("Set the environmental variables: ")
    print("")
    print("    Required: <PLUGID> is the Device ID e.g. 01234567891234567890")
    print("              <PLUGIP> is the IP address of the smart plug e.g. 10.0.1.99")
    print("    Optional: <PLUGKEY> is the Device Key (default 0123456789abcdef)")
    print("              <PLUGVERS> is the Firmware Version 3.1 (default), 3.2, 3.3, 3.4 or 3.5")
    print("              <PLUGJSON> set to 'yes' for JSON output")
    print("")
    print("    Example:")
    print("              docker run -e PLUGID=\"01234567891234567890\" \\")
    print("                         -e PLUGIP=\"10.0.1.x\" \\")
    print("                         -e PLUGKEY=\"0123456789abcdef\" \\")
    print("                         -e PLUGVERS=\"3.3\" \\")
    print("                         jasonacox/tuyapower")
    print("")
    exit()
DEVICEID = sys.argv[1] if len(sys.argv) >= 2 else "01234567891234567890"
DEVICEIP = sys.argv[2] if len(sys.argv) >= 3 else "10.0.1.99"
DEVICEKEY = sys.argv[3] if len(sys.argv) >= 4 else "0123456789abcdef"
DEVICEVERS = sys.argv[4] if len(sys.argv) >= 5 else "3.1"
DEVICEJSON = sys.argv[5] if len(sys.argv) >= 6 else "no"

# Check for environmental variables and always use those if available (required for Docker)
PLUGID = os.getenv("PLUGID", DEVICEID)
PLUGIP = os.getenv("PLUGIP", DEVICEIP)
PLUGKEY = os.getenv("PLUGKEY", DEVICEKEY)
PLUGVERS = os.getenv("PLUGVERS", DEVICEVERS)
PLUGJSON = os.getenv("PLUGJSON", DEVICEJSON).lower()=="yes"

now = datetime.datetime.utcnow()
iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

# Poll Smart Device for Raw  Data
(raw) = tuyapower.deviceRaw(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)
# Poll Smart Switch for Power Data
(on, w, mA, V, err) = tuyapower.deviceInfo(PLUGID, PLUGIP, PLUGKEY, PLUGVERS)

# Compute projected kWh
day = (w / 1000.0) * 24
week = 7.0 * day
month = (week * 52.0) / 12.0

# Print Output
if not PLUGJSON:
    # Print friendly output
    print("TuyaPower (Tuya Power Stats) [%s] %s [%s]"%(tuyapower.__version__,tuyapower.api,tuyapower.api_ver))
    print("\nDevice %s at %s key %s protocol %s:" % (PLUGID,PLUGIP,PLUGKEY,PLUGVERS))
    print("    Response Data: %s" % raw)
    if isinstance(on,dict):
        print("    Switches (%d) On: %s" % (len(on),on))
    else:
        print("    Switch On: %r" % on)
    if err == "OK":
        print("    Power (W): %f" % w)
        print("    Current (mA): %f" % mA)
        print("    Voltage (V): %f" % V)
        print("    Projected usage (kWh):  Day: %f Week: %f  Month: %f" % (day,week,month))
    else:
        print("    NOTE: %s" % err)
    print("")
else: 
    # Print json output
    print(
        '{ "datetime": "%s", "switch": "%s", "power": "%s", "current": "%s", "voltage": "%s" }'
        % (iso_time, on, w, mA, V)
    )
