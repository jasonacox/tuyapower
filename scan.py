#!/usr/bin/python
#
# TuyaScan - Scan for tuya devices on the network broadcasting on UDP port 6666 and 6667
# 
# Author: Jason A. Cox
# For more information see https://github.com/jasonacox/tuyapower

from __future__ import print_function
import json
import socket
from hashlib import md5
from Crypto.Cipher import AES  # PyCrypto

MAXCOUNT = 10       # How many tries before stopping
DEBUG = False       # Additional details beyond verbose
UDPPORT = 6666      # Tuya 3.1 UDP Port
UDPPORTS = 6667     # Tuya 3.3 encrypted UDP Port
TIMEOUT = 3.0       # Seconds to wait for a broadcast

# Return positive number or zero
def floor(x):
    if x > 0:
            return x
    else:
            return 0

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
    devices[newdevice['ip']] = newdevice
    return False

# Scan function
def deviceScan(verbose = False):
    """Scans your network for smart plug devices on UDP ports 6666 and 6667
        devices = tuyapower.deviceScan(verbose)

    Parameters:
        verbose = True or False, print formatted output to stdout

    Response: 
        devices = Dictionary of all devices found with power data if available

    To unpack data, you can do something like this:

        devices = tuyapower.deviceScan()
        for ip in devices:
            id = devices[ip]['gwId']
            key = devices[ip]['productKey']
            vers = devices[ip]['version']

    """
     # Enable UDP lisenting broadcasting mode on UDP port 6666 - 3.1 Devices
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", UDPPORT))
    client.settimeout(TIMEOUT) 
    # Enable UDP lisenting broadcasting mode on encrypted UDP port 6667 - 3.3 Devices
    clients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    clients.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    clients.bind(("", UDPPORTS))
    clients.settimeout(TIMEOUT)

    if(verbose):
        print("Scanning on UDP ports %d and %d for devices...\n"%(UDPPORT,UDPPORTS))

    # globals
    devices={}
    count = 0
    counts = 0
    spinnerx = 0
    spinner = "|/-\\|"

    # loop to find devices
    while (count + counts) <= MAXCOUNT:
        note = 'invalid'
        print("Scanning... %s\r"%(spinner[spinnerx]), end = '')
        spinnerx = (spinnerx + 1) % 4

        if (count <= counts):  # alternate between 6666 and 6667 ports
            try:
                data, addr = client.recvfrom(4048)
            except:
                # Timeout
                count = count + 1
                continue
        else:
            try:
                data, addr = clients.recvfrom(4048)
            except:
                # Timeout
                counts = counts + 1
                continue
            
        if(DEBUG): 
            print("* Message from [%s]: %s\n"%addr,data)
        ip = addr[0]
        gwId = productKey = version = ""
        result = data
        try: 
            result = data[20:-8]
            try:
                result = decrypt_udp(result)  # 3.3
            except:
                result = result.decode()      # 3.1

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

        # check to see if we have seen this device before and add to devices array
        if appenddevice(result, devices) == False:
            # new device found - back off count if we keep getting new devices
            if(version=='3.1'):
                count = floor(count - 1)
            else:
                counts = floor(counts - 1)
            if(verbose):
                print("FOUND Device [%s payload]: %s\n    ID = %s, productKey = %s, Version = %s" % (note,ip,gwId,productKey,version))
        else:
            # no new devices found
            if(version=='3.1'):
                count = count + 1
            else:
                counts = counts + 1

    if(verbose):
        print("                 \nScan Complete!  Found %s devices.\n"%len(devices))
        
    return(devices)


d = deviceScan(True)  