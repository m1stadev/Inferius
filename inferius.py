#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import ipsw
import sys
import subprocess
import time

assert ('darwin' in sys.platform), "This script can only be ran on macOS. Please run this on a macOS computer."

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ipsw', help='specify IPSW')
parser.add_argument('-v', '--verbose', help='print verbose output', action='store_true')
args = parser.parse_args()

if args.ipsw:
    input('Please make sure your device is connected, then press enter: ')

    ideviceinfo_model_process = subprocess.Popen('./resources/bin/ideviceinfo -s | /usr/bin/grep HardwareModel', stdout=subprocess.PIPE, shell=True)
    hardware_model = str(ideviceinfo_model_process.stdout.read())
    if len(hardware_model) == 3:
            print('No device is connected, exiting!')
            exit()
    ideviceinfo_model_process = subprocess.Popen('./resources/bin/ideviceinfo -s | /usr/bin/grep ProductType', stdout=subprocess.PIPE, shell=True)
    device_identifier = str(ideviceinfo_model_process.stdout.read())
    if len(device_identifier) == 3:
            print('No device is connected, exiting!')
            exit()
    device_identifier = device_identifier[13:-3]
    print(f'extracting IPSW at this -> {args.ipsw}')
    if args.verbose:
        print(f'extracting IPSW: {args.ipsw}')
        ipsw_dir = ipsw.extract_ipsw(args.ipsw, 'yes')
    else:
        ipsw_dir = ipsw.extract_ipsw(args.ipsw)
    print('IPSW extracted! Grabbing ramdisk...')
    if args.verbose:
        ramdisk = ipsw.find_ramdisk(ipsw_dir, 'yes')
    else:
        ramdisk = ipsw.find_ramdisk(ipsw_dir)
    print('Ramdisk found! Extracting asr...')
    if args.verbose:
        ipsw.extract_asr(ramdisk, 'yes')
    else:
        ipsw.extract_asr(ramdisk)
    print('Grabbing bootchain to patch...')
    if args.verbose:
        ipsw.find_bootchain(ipsw_dir, hardware_model, device_identifier, 'yes')
    else:
        ibss, ibec, kernelcache = ipsw.find_bootchain(ipsw_dir, hardware_model, device_identifier)
    
