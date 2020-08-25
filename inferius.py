#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import ipsw, patch
import sys
import subprocess
import requests
import platform
import time
import json

if platform.system() == 'Darwin':
    pass
else:
    sys.exit('This script can only be ran on macOS. Please run this on a macOS computer.')

parser = argparse.ArgumentParser(description='Inferius - Create custom IPSWs for your 64bit iOS device!', usage="./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW' [-v]")
parser.add_argument('-d', '--device', help='Your device identifier (e.g. iPhone10,2)', nargs=1)
parser.add_argument('-i', '--version', help='The version of your stock IPSW', nargs=1)
parser.add_argument('-f', '--ipsw', help='Path to custom IPSW', nargs=1)
parser.add_argument('-v', '--verbose', help='Print verbose output for debugging', action='store_true')
args = parser.parse_args()

if args.ipsw:
    if args.device:
        pass
    else:
        sys.exit('Error: You must specify a device identifier!\nExiting...')
    if args.version:
        version_str = args.version[0]
        if version_str.startswith('10.'):
            sys.exit('Error: iOS 10.x IPSWs are not currently supported!\nExiting...')
    else:
        sys.exit('Error: You must specify an iOS version!\nExiting...')
    if args.verbose:
        print('[VERBOSE] Checking for required dependencies...')
    ldid_check = subprocess.Popen('/usr/bin/which ldid2', stdout=subprocess.PIPE, shell=True) # Dependency checking
    time.sleep(5)
    output = str(ldid_check.stdout.read())
    if len(output) == 3:
        sys.exit('Error: ldid not installed! Please install ldid from Homebrew, then run this script again.')
    if os.path.exists(f'work'): # In case work directory is still here from a previous run, remove it
        shutil.rmtree(f'work')
    print(f'Finding Firmware bundle for {args.device[0]}, {args.version[0]}...')
    if args.verbose:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0], 'yes')
    else:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0])
    if args.verbose:
        print('Checking if device is A9...')
    is_a9 = ipsw.a9_check(firmware_bundle)
    if is_a9:
        if args.verbose:
            print('Device is A9, fetching correct board config...')
        board_configs = ipsw.fetch_a9_boardconfigs(firmware_bundle)
        if len(board_configs) != 2:
            sys.exit('Firmware Bundle for A9 is invalid.\nExiting...')
        firm_bundle_number = input(f'A9 device detected, please choose the correct board config for your device:\n[1] {board_configs[0]}\n[2] {board_configs[1]}\nChoice: ')
        try:
            int(firm_bundle_number)
        except ValueError:
            sys.exit('Input not a number!.\nExiting...')
        firm_bundle_number = int(firm_bundle_number)
        if 0 < firm_bundle_number < 3:
            firm_bundle_number = firm_bundle_number - 1
            pass
        else:
            sys.exit('Invalid input given.\nExiting...')
    else:
        firm_bundle_number = 1337
        if args.verbose:
            print('Device is not A9, continuing...')

    if args.verbose:
        ipsw_dir = ipsw.extract_ipsw(args.ipsw[0], 'yes')
    else:
        ipsw_dir = ipsw.extract_ipsw(args.ipsw[0])
    print('IPSW extracted! Applying patches to bootchain...')
    if args.verbose:
        patch.patch_bootchain(firmware_bundle, ipsw_dir, firm_bundle_number, 'yes')
    else:
        patch.patch_bootchain(firmware_bundle, ipsw_dir, firm_bundle_number)
    print('Grabbing latest LLB and iBoot to put into custom IPSW...')
    ipsw.grab_latest_llb_iboot(ipsw_dir, firmware_bundle, firm_bundle_number)
    print('Packing everything into custom IPSW. This may take a while, please wait...')
    if args.verbose:
        ipsw_name = ipsw.make_ipsw(ipsw_dir, firmware_bundle, 'yes')
    else:
        ipsw_name = ipsw.make_ipsw(ipsw_dir, firmware_bundle)
    print(f'Done!\nCustom IPSW at: {ipsw_name}')
    print('Cleaning up...')
    shutil.rmtree('work')
else:
    exit(parser.print_help(sys.stderr))