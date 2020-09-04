# TuyaPower Module
# -*- coding: utf-8 -*-
"""
 Python module to pull power and state data from Tuya WiFi smart devices

 Author: Jason A. Cox
 For more information see https://github.com/jasonacox/tuyapower

 This will run if calling this module via command line:  
    python -m tuyapower
"""
import tuyapower
import sys

retries = 0

print("TuyaPower (Tuya compatible smart plug scanner) [%s] %s [%s]\n"%(tuyapower.version,tuyapower.api,tuyapower.api_ver))

try:
    if len(sys.argv) > 1:
        retries = int(sys.argv[1])
except:
    print("Usage: python -m tuyapower <max_retry>")
    sys.exit(2)

if retries > 0:
    tuyapower.scan(retries)
else:
    tuyapower.scan()
