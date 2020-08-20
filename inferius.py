#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import ipsw, patch
import sys
import subprocess
import time
import requests
import platform

if platform.system() == 'Darwin':
    pass
else:
    exit("This script can only be ran on macOS. Please run this on a macOS computer.")

parser = argparse.ArgumentParser(description='Inferius - Create and restore custom IPSWs to your 64bit iOS device!', usage="./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW'")
parser.add_argument('-f', '--ipsw', help='Stock IPSW to create into a custom IPSW', nargs=1)
parser.add_argument('-d', '--device', help='Your device identifier (e.g. iPhone10,2)', nargs=1)
parser.add_argument('-i', '--version', help='The version of your stock IPSW', nargs=1)
parser.add_argument('-v', '--verbose', help='Print verbose output for debugging', action='store_true')
args = parser.parse_args()

if args.ipsw:
    if args.device:
        pass
    else:
        sys.exit('Error: You must specify a device identifier with -d!\nExiting...')
    if args.version:
        pass
    else:
        sys.exit('Error: You must specify an iOS version with -i!\nExiting...')
    if args.verbose:
        print('Checking for required dependencies...')
    homebrew_check_process = subprocess.Popen('/usr/bin/which brew', stdout=subprocess.PIPE, shell=True) # Dependency checking
    output = str(homebrew_check_process.stdout.read())
    if len(output) == 3:
        print('Homebrew not installed! Please go to https://brew.sh/ and install Homebrew.')
        sys.exit()
    bsdiff_check_process = subprocess.Popen('/usr/bin/which bspatch', stdout=subprocess.PIPE, shell=True)
    output = str(bsdiff_check_process.stdout.read())
    if len(output) == 3:
        print("bsdiff not installed! Run 'brew install bsdiff'.")
        sys.exit()
    if os.path.exists(f'work'): # In case work directory still remains, remove it
        shutil.rmtree(f'work')
    print(f'Finding Firmware bundle for:\nDevice: {args.device[0]}\niOS: {args.version[0]}')
    if args.verbose:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0], 'yes')
    else:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0])
    if args.verbose:
        print(f'extracting IPSW: {args.ipsw[0]}')
        ipsw_dir = ipsw.extract_ipsw(args.ipsw[0], 'yes')
    else:
        ipsw_dir = ipsw.extract_ipsw(args.ipsw[0])
    print('IPSW extracted! Grabbing ramdisk...')
    if args.verbose:
        ramdisk = ipsw.grab_ramdisk(ipsw_dir, firmware_bundle, 'yes')
    else:
        ramdisk = ipsw.grab_ramdisk(ipsw_dir, firmware_bundle)
    print('Ramdisk found! Extracting asr...')
    if args.verbose:
        ipsw.extract_asr(ramdisk, 'yes')
    else:
        ipsw.extract_asr(ramdisk)
    print('Grabbing bootchain to patch...')
    if args.verbose:
        ibss_path, ibec_path, kernelcache_path = ipsw.grab_bootchain(ipsw_dir, firmware_bundle, 'yes')
    else:
        ibss_path, ibec_path, kernelcache_path = ipsw.grab_bootchain(ipsw_dir, firmware_bundle)
    print('Patching bootchain...')
    print('not implemented yet.')
else:
    exit(parser.print_help(sys.stderr))
