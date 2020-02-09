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

print("TuyaPower (Tuya compatible smart plug scanner) [%s]\n"%tuyapower.version)
tuyapower.scan()