#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
import subprocess
import platform
from resources import ipsw, patch, restore
import glob
import time

if platform.system() == 'Darwin':
    pass
else:
    sys.exit('This script can only be ran on macOS. Please run this on a macOS computer.')

parser = argparse.ArgumentParser(description='Restituere - Restore custom IPSWs to your 64bit iOS device!', usage="./restituere.py -d 'device' -i 'iOS version' -f 'IPSW' [-v]")
parser.add_argument('-d', '--device', help='Your device identifier (e.g. iPhone10,2)', nargs=1)
parser.add_argument('-i', '--version', help='The version of your custom IPSW', nargs=1)
parser.add_argument('-f', '--ipsw', help='Custom IPSW to restore onto your device', nargs=1)
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
    device_check = input('Is your device is connected in Pwned DFU mode with signature checks removed? [Y/N]: ')
    if 'Y' or 'y' in device_check.lower():
        pass
    else:
        sys.exit('Exiting...')
    lsusb = subprocess.Popen('./resources/bin/lsusb', stdout=subprocess.PIPE, shell=True)
    time.sleep(10)
    lsusb_output = str(lsusb.stdout.read())
    if 'Apple Mobile Device (DFU)' in lsusb_output:
        pass
    else:
        sys.exit('Device not found!\nExiting...')
    device_identifier = args.device[0]
    device_identifier = device_identifier.lower()
    if device_identifier.startswith('iphone8') or device_identifier == 'ipad6,11' or device_identifier == 'ipad6,12':
        sys.exit('Error: A9 devices are currently not supported!\nExiting...') #TODO: Implement A9 support
    else:
        pass
    print('Fetching some required info...')
    if args.verbose:
        print('[VERBOSE] Fetching ECID...')
    fetch_ecid = subprocess.Popen('./resources/bin/igetnonce | grep ECID', stdout=subprocess.PIPE, shell=True)
    time.sleep(3)
    ecid = str(fetch_ecid.stdout.read())
    ecid = ecid[7:-3]
    dec_ecid = str(int(ecid, 16))
    if args.verbose:
        print(f'[VERBOSE] ECID: {ecid}')
    if args.verbose:
        print('[VERBOSE] Fetching apnonce...')
    fetch_apnonce = subprocess.Popen('./resources/bin/igetnonce | grep ApNonce', stdout=subprocess.PIPE, shell=True)
    time.sleep(3)
    apnonce = str(fetch_apnonce.stdout.read())
    apnonce = apnonce[10:-3]
    if args.verbose:
        print(f'[VERBOSE] apnonce: {apnonce}')
    if os.path.exists(f'work'): # In case work directory is still here from a previous run, remove it
        shutil.rmtree(f'work')
    os.makedirs('work/ipsw', exist_ok = True)
    print('Saving SHSH blobs for restore...')
    if len(glob.glob('work/ipsw/*.shsh2')) != 0:
        for shsh in glob.glob('work/ipsw/*.shsh2'):
            os.remove(shsh)
    subprocess.run(f'./resources/bin/tsschecker -d {args.device[0]} -l -e 0x{ecid} -s --apnonce {apnonce} --save-path work/ipsw/', stdout=open('resources/restituere.log','w'), shell=True)
    if len(glob.glob('work/ipsw/*.shsh2')) == 0:
        sys.exit("SHSH Blobs didn't save! Make sure you're connected to the internet, then try again.\nExiting...")
    for shsh in glob.glob('work/ipsw/*.shsh2'):
        os.rename(shsh, 'work/ipsw/blob.shsh2')
    print('SHSH blobs saved!')
    if args.verbose:
        print(f'Finding Firmware bundle for {args.device[0]}, {args.version[0]}...')
    if args.verbose:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0], 'yes')
    else:
        firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0])
    if args.verbose:
        print('Extracting iBSS and iBEC from custom IPSW...')
    if args.verbose:
        ibss_path, ibec_path = ipsw.extract_ibss_ibec(args.ipsw[0], firmware_bundle, 'yes')
    else:
        ibss_path, ibec_path = ipsw.extract_ibss_ibec(args.ipsw[0], firmware_bundle)
    print('Signing iBSS and iBEC with SHSH blob...')
    if args.verbose:
        patch.sign_ibss_ibec(ibss_path, ibec_path, 'yes')
    else:
        patch.sign_ibss_ibec(ibss_path, ibec_path)
    print('Preparations done! Beginning restore...')
    if args.verbose:
        restore.send_ibss_ibec('yes')
    else:
        restore.send_ibss_ibec()
    if args.verbose:
        restore.restore(args.ipsw[0], restore.is_cellular(device_identifier), 'yes')
    else:
        restore.restore(args.ipsw[0], restore.is_cellular(device_identifier))
else:
    exit(parser.print_help(sys.stderr))