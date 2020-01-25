#!/usr/bin/python
#
# TuyaScan - Scan for tuya devices on the network broadcasting on UDP port 6666
# 
# Author: Jason A. Cox
# For more information see https://github.com/jasonacox/tuyapower

import json
import socket

try:
    #raise ImportError
    import Crypto
    from Crypto.Cipher import AES  # PyCrypto
except ImportError:
    Crypto = AES = None
    import pyaes  # https://github.com/ricmoo/pyaes

MAXCOUNT = 10
PORT = 6666
PROTOCOL_VERSION_BYTES_31 = b'3.1'
PROTOCOL_VERSION_BYTES_33 = b'3.3'

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print("Scanning on UDP port %s for devices...\n"%PORT)

def appenddevice(newdevice, devices):
    for i in devices:
        if i['ip'] == newdevice['ip']:
                return True
    devices.append(newdevice)
    return False

devices=[]
count = 0
stop = False

client.bind(("", PORT))
while stop == False:
    data, addr = client.recvfrom(4048)
    # print("MESSAGE from [%s]: %s"%addr,data)
    ip = addr[0]
    gwId = productKey = version = ""
    result = data
    try: 
        result = data[20:-8]
        note = 'Valid '
        if result.startswith(b'{'):
            # this is the regular expected code path
            if not isinstance(result, str):
                result = result.decode()
            result = json.loads(result)
        else:
            # print('Unexpected payload=%r', result)
            note = 'Invalid '
            result = {"ip": ip}

        ip = result['ip']
        gwId = result['gwId']
        productKey = result['productKey']
        version = result['version']
    except:
        #print("! Bad data !")
        result = {"ip": ip}

    if appenddevice(result, devices) == False:
        print("FOUND [%s payload]: %s, ID = %s, Key = %s, Version = %s" % (note,ip,gwId,productKey,version))
    else:
        count = count + 1
        if count > MAXCOUNT: 
            stop = True

print("\nScan Complete!  Found %s devices."%len(devices))
