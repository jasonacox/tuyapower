#!/usr/bin/python
#
# TuyaScan - Scan for tuya devices on the network broadcasting on UDP port 6666 and 6667
# 
# Author: Jason A. Cox
# For more information see https://github.com/jasonacox/tuyapower

import json
import socket
from hashlib import md5

try:
    #raise ImportError
    import Crypto
    from Crypto.Cipher import AES  # PyCrypto
except ImportError:
    Crypto = AES = None
    import pyaes  # https://github.com/ricmoo/pyaes

MAXCOUNT = 10
DEBUG = False

# UDP packet payload decryption - credit to tuya-convert 
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
encrypt = lambda msg, key: AES.new(key, AES.MODE_ECB).encrypt(pad(msg).encode())
decrypt = lambda msg, key: unpad(AES.new(key, AES.MODE_ECB).decrypt(msg)).decode()
udpkey = md5(b"yGAdlopoPVldABfn").digest()
decrypt_udp = lambda msg: decrypt(msg, udpkey)

# Store found devices in memory
def appenddevice(newdevice, devices):
    if(newdevice['ip'] in devices):
        return True
    """
    for i in devices:
        if i['ip'] == newdevice['ip']:
                return True
    """
    devices[newdevice['ip']] = newdevice
    return False

# Scan function
def deviceScan(verbose = False, port = 6666):
    """Scans your network for smart plug devices
        devices = tuyapower.deviceScan(verbose, port)

    Parameters:
        verbose = True or False, print formatted output to stdout
        port = UDP port to scan (default 6666) 

    Response: 
        devices = Dictionary of all devices found with power data if available

    To unpack data, you can do something like this:

        devices = tuyapower.deviceScan()
        for ip in devices:
            id = devices[ip]['gwId']
            key = devices[ip]['productKey']
            vers = devices[ip]['version']
            (on, w, mA, V, err) = deviceInfo(id, ip, key, vers)
            print("Device at %s: ID %s, state=%s, W=%s, mA=%s, V=%s [%s]"%(ip,id,on,w,mA,V,err))

    """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    # client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    if(verbose):
        print("Scanning on UDP port %s for devices...\n"%port)
    devices={}
    count = 0
    stop = False

    client.bind(("", port))
    while stop == False:
        note = 'invalid'
        data, addr = client.recvfrom(4048)
        if(DEBUG): 
            print("* Message from [%s]: %s\n"%addr,data)
        ip = addr[0]
        gwId = productKey = version = ""
        result = data
        try: 
            result = data[20:-8]
            try:
                result = decrypt_udp(result)
            except:
                result = result.decode()

            result = json.loads(result)

            note = 'Valid'
            ip = result['ip']
            gwId = result['gwId']
            productKey = result['productKey']
            version = result['version']
        except:
            if(DEBUG):
                print("*  Unexpected payload=%r\n", result)
            result = {"ip": ip}
            note = "Unknown"

        if appenddevice(result, devices) == False:
            if(verbose):
                print("FOUND Device [%s payload]: %s\n    ID = %s, productKey = %s, Version = %s" % (note,ip,gwId,productKey,version))
        else:
            count = count + 1
            if count > MAXCOUNT: 
                stop = True

    if(verbose):
        print("\nScan Complete!  Found %s devices.\n"%len(devices))
        
    return(devices)


d = deviceScan(True, 6666)
d = deviceScan(True, 6667)