#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import ipsw
import sys
import subprocess
import time
import requests

print('Inferius - Create and restore custom IPSWs to your 64bit iOS device!')

assert ('darwin' in sys.platform), "This script can only be ran on macOS. Please run this on a macOS computer."

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ipsw', help='specify IPSW')
parser.add_argument('-v', '--verbose', help='print verbose output', action='store_true')
args = parser.parse_args()

if args.ipsw:
    print('Checking for required dependencies...')
    homebrew_check_process = subprocess.Popen('/usr/bin/which brew', stdout=subprocess.PIPE, shell=True)
    output = str(homebrew_check_process.stdout.read())
    if len(output) == 3:
        print('Homebrew not installed! Please go to https://brew.sh/ and install Homebrew.')
        exit()
    bsdiff_check_process = subprocess.Popen('/usr/bin/which bspatch', stdout=subprocess.PIPE, shell=True)
    output = str(bsdiff_check_process.stdout.read())
    if len(output) == 3:
        print("bsdiff not installed! Run 'brew install bsdiff'.")
        exit()
    ideviceinfo_check_process = subprocess.Popen('/usr/bin/which ideviceinfo', stdout=subprocess.PIPE, shell=True)
    output = str(ideviceinfo_check_process.stdout.read())
    if len(output) == 3:
        print("libimobiledevice not installed! Run 'brew install libimobiledevice'.")
        exit()
    grep_check_process = subprocess.Popen('/usr/bin/which grep', stdout=subprocess.PIPE, shell=True)
    output = str(ideviceinfo_check_process.stdout.read())
    if len(output) == 3:
        print("grep not installed! Run 'brew install grep'.")
        exit()
    pzb_check_process = subprocess.Popen('/usr/bin/which pzb', stdout=subprocess.PIPE, shell=True)
    output = str(pzb_check_process.stdout.read())
    if os.path.isfile('resources/bin/pzb'):
        pass
    elif len(output) == 3:
        print('partialZipBrowser not installed! Downloading binary manually...')
        try:
            dl = requests.get('https://github.com/tihmstar/partialZipBrowser/releases/download/36/buildroot_macos-latest.zip', allow_redirects=True)
        except:
            print('Unable to download binary, make sure you are connected to the internet!\nExiting...')
            exit()
        os.makedirs('resources/tmp', exist_ok=True)
        open('resources/tmp/buildroot_macos-latest.zip', 'wb').write(dl.content)
        shutil.unpack_archive('resources/tmp/buildroot_macos-latest.zip', 'resources/tmp/buildroot_macos-latest', 'zip')
        shutil.copyfile('resources/tmp/buildroot_macos-latest/buildroot_macos-latest/usr/local/bin/pzb', 'resources/bin/pzb')
        shutil.rmtree('resources/tmp', ignore_errors=True)
        
    
    input('Please make sure your device is connected, then press enter: ')
    ideviceinfo_model_process = subprocess.Popen('ideviceinfo -s | grep HardwareModel', stdout=subprocess.PIPE, shell=True)
    hardware_model = str(ideviceinfo_model_process.stdout.read())
    if len(hardware_model) == 3:
            print('No device detected, exiting!')
            exit()
    ideviceinfo_model_process = subprocess.Popen('ideviceinfo -s | grep ProductType', stdout=subprocess.PIPE, shell=True)
    device_identifier = str(ideviceinfo_model_process.stdout.read())
    if len(device_identifier) == 3:
            print('No device detected, exiting!')
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
    
