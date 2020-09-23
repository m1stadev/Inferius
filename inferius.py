#!/usr/bin/env python3

from resources import ipsw, patch, inferius_restore, utils
import argparse
import atexit
import glob
import json
import os
import platform
import requests
import shutil
import subprocess
import sys
import time

if not platform.system() == 'Darwin':
    sys.exit('[ERROR] This script can only be ran on macOS. Please run this on a macOS computer.\nExiting...')

if not platform.architecture()[0] == '64bit':
    sys.exit('[ERROR] This script can only be ran on a 64bit computer.\nExiting...')

parser = argparse.ArgumentParser(description='Inferius - Create custom IPSWs for your 64bit iOS device!', usage="./inferius.py -d 'device' -i 'iOS version' -f 'IPSW' [-c/-r] [-v]")
parser.add_argument('-c', '--create', help='Create custom IPSW', action='store_true')
parser.add_argument('-d', '--device', help='Device identifier (e.g. iPhone10,2)', nargs=1)
parser.add_argument('-f', '--ipsw', help='Path to custom IPSW', nargs=1)
parser.add_argument('-i', '--version', help='The version of your stock IPSW', nargs=1)
parser.add_argument('-r', '--restore', help='Restore custom IPSW after creation', action='store_true')
parser.add_argument('-u', '--update', help='Restore device without losing data (requires --restore)', action='store_true')
parser.add_argument('-v', '--verbose', help='Print verbose output for debugging', action='store_true')
args = parser.parse_args()

def create_ipsw():
    utils.print_and_log('Verifying IPSW. This may take a while, please wait...', True)
    is_stock = ipsw.verify_ipsw(args.device[0], args.version[0], args.ipsw[0], is_verbose)
    if not is_stock:
        sys.exit(f'[ERROR] IPSW {args.ipsw[0]} is not verified! Redownload your IPSW, and try again.\nExiting...')

    ipsw.extract_ipsw(args.ipsw[0], is_verbose)
    utils.print_and_log('IPSW extracted! Verifying bootchain...', True)

    ipsw.verify_bootchain(firmware_bundle, firm_bundle_number, is_verbose)

    utils.print_and_log('Bootchain verified! Patching bootchain...', True)
    patch.patch_bootchain(firmware_bundle, firm_bundle_number, is_verbose)

    utils.print_and_log('Grabbing latest LLB and iBoot to put into custom IPSW...', True)
    ipsw.grab_latest_llb_iboot(args.device[0], firmware_bundle, firm_bundle_number)

    utils.print_and_log('Packing everything into custom IPSW. This may take a while, please wait...', True)
    ipsw_name = ipsw.make_ipsw(firmware_bundle, is_verbose)

    utils.print_and_log('Cleaning up...', True)
    if args.restore:
        utils.print_and_log(f'Custom IPSW at: {ipsw_name}', True)
    else:
        utils.print_and_log(f'Done!\nCustom IPSW at: {ipsw_name}', True)

    utils.cleanup(is_verbose)

    return ipsw_name

def restore(fresh_ipsw, ipsw_path):
    processor = ipsw.fetch_processor(firmware_bundle)

    utils.print_and_log('Checking if IPSW is custom...', False)
    is_stock = ipsw.verify_ipsw(args.device[0], args.version[0], ipsw_path, is_verbose)
    if is_stock:
        utils.print_and_log('[ERROR] IPSW is not custom, will not restore!\nExiting...', False)
        sys.exit()

    if fresh_ipsw:
        utils.log('------------RESTORE-BEGINNING------------')
        utils.print_and_log('Restoring freshly created custom IPSW', is_verbose)
    else:
        utils.print_and_log('Checking if IPSW is custom...', False)
        is_stock = ipsw.verify_ipsw(args.device[0], args.version[0], ipsw_path, is_verbose)
        if is_stock:
            utils.print_and_log('[ERROR] IPSW is not custom, will not restore!\nExiting...', False)
            sys.exit()

    if args.update:
        keep_data = True
    else:
        keep_data = False

    device_check = input('Is your device is connected in Pwned DFU mode with signature checks removed? [Y/N]: ')
    utils.print_and_log(f'Is your device is connected in Pwned DFU mode with signature checks removed? [Y/N]: {device_check}', False)

    if not 'y' in device_check.lower():
        utils.print_and_log('[ERROR] Specified device is not in pwndfu!\nExiting...', is_verbose)
        sys.exit()

    lsusb = subprocess.run('./resources/bin/lsusb', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(lsusb.stdout)

    if not 'Apple Mobile Device (DFU Mode)' in lsusb.stdout:
        utils.print_and_log('[ERROR] Specified device is not in pwndfu!\nExiting...', is_verbose)
        sys.exit()

    utils.print_and_log('Fetching some required info...', True)

    utils.print_and_log('[VERBOSE] Fetching ECID...', is_verbose)
    fetch_ecid = subprocess.run('./resources/bin/igetnonce | grep ECID', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(fetch_ecid.stdout)
    ecid = fetch_ecid.stdout[5:-1]
    utils.print_and_log(f'[VERBOSE] ECID: 0x{ecid}', is_verbose)

    utils.print_and_log('[VERBOSE] Fetching apnonce...', is_verbose)
    fetch_apnonce = subprocess.run('./resources/bin/igetnonce | grep ApNonce', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(fetch_apnonce.stdout)
    apnonce = fetch_apnonce.stdout[8:-1]
    utils.print_and_log(f'[VERBOSE] apnonce: {apnonce}', is_verbose)

    os.makedirs('work/ipsw', exist_ok=True)

    if firm_bundle_number != 1337:
        fetch_blobs = subprocess.run(f'./resources/bin/tsschecker -d {args.device[0]} -l -B {board_configs[firm_bundle_number]}ap -e 0x{ecid} -s --apnonce {apnonce} --save-path work/ipsw/', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    else:
        fetch_blobs = subprocess.run(f'./resources/bin/tsschecker -d {args.device[0]} -l -e 0x{ecid} -s --apnonce {apnonce} --save-path work/ipsw/', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(fetch_blobs.stdout)
    
    if not 'Saved shsh blobs!' in fetch_blobs.stdout:
        utils.print_and_log("[ERROR] SHSH didn't save! Make sure you're connected to the internet, then try again.\nExiting...", True)
        sys.exit()

    for shsh in glob.glob('work/ipsw/*.shsh2'):
        os.rename(shsh, 'work/ipsw/blob.shsh2')
    utils.print_and_log('SHSH blobs saved!', True)

    utils.print_and_log('Extracting iBSS and iBEC from custom IPSW...', True)
    ibss_path, ibec_path = ipsw.extract_ibss_ibec(ipsw_path, firmware_bundle, firm_bundle_number, is_verbose)

    utils.print_and_log('Signing iBSS and iBEC with SHSH blob...', True)
    patch.sign_ibss_ibec(ibss_path, ibec_path, is_verbose)

    utils.print_and_log('Preparations done! Beginning restore...', True)
    inferius_restore.send_bootchain(processor, is_verbose)
    inferius_restore.restore(ipsw_path, inferius_restore.is_cellular(args.device[0]), keep_data, is_verbose)

    utils.print_and_log('Restore finished! Cleaning up...', True)
    utils.cleanup(is_verbose)
    utils.print_and_log('Done.\nExiting...', True)

if not args.ipsw:
    sys.exit(parser.print_help(sys.stderr))

if args.device:
    utils.log('Inferius Log')
    utils.log(f'[INFO] Device: {args.device[0]}')
else:
    sys.exit(parser.print_help(sys.stderr))

if args.version:
    version_str = args.version[0]
    version_str = version_str.split('.')
    unsupported_versions = ['1', '2', '3', '4', '5', '6' '7' '8' '9' '10']
    major_ios = f'{version_str[0]}'

    if major_ios in unsupported_versions:
        sys.exit(f'[ERROR] iOS {major_ios}.x downgrades are not currently supported!\nExiting...')

else:
    sys.exit(parser.print_help(sys.stderr))
utils.log(f'[INFO] iOS Version: {args.version[0]}')

if args.verbose:
    is_verbose = True
else:
    is_verbose = False

if not utils.check_internet():
    sys.exit('[ERROR] You are not connected to the Internet. Connect to the internet, then run this script again.\nExiting...')

atexit.register(utils.cleanup, 'exit')

utils.cleanup(is_verbose)

utils.print_and_log(f'[VERBOSE] Finding Fimware Bundle for {args.device[0]}, {args.version[0]}', is_verbose)
firmware_bundle = ipsw.find_bundle(args.device[0], args.version[0], is_verbose)

utils.print_and_log('[VERBOSE] Checking if device is A9...', is_verbose)
if ipsw.is_a9(firmware_bundle):
    utils.print_and_log('[VERBOSE] Device is A9, fetching correct board config...', is_verbose)

    board_configs = ipsw.fetch_boardconfig(firmware_bundle)
    if len(board_configs) != 2:
        utils.print_and_log('[ERROR] Firmware Bundle is invalid.\nExiting...', True)
        sys.exit()

    firm_bundle_number = input(f'A9 device detected, please choose the number of the correct board config for your device:\n  [1] {board_configs[0]}ap\n  [2] {board_configs[1]}ap\nChoice: ')
    utils.log(f'A9 device detected, please choose the number of the correct board config for your device:\n  [1] {board_configs[0]}ap\n  [2] {board_configs[1]}ap\nChoice: {firm_bundle_number}')

    try:
        int(firm_bundle_number)
    except ValueError:
        utils.print_and_log('[Error] Input not a number!\nExiting...', True)
        sys.exit()
    
    utils.log(f'[INFO] Firmware bundle number: {firm_bundle_number}')
    firm_bundle_number = int(firm_bundle_number)
    if 0 < firm_bundle_number < 3:
        firm_bundle_number = firm_bundle_number - 1
    else:
        utils.print_and_log('[ERROR] Invalid input given.\nExiting...', True)
        sys.exit()

    utils.log(f'[INFO] Device boardconfig: {board_configs[firm_bundle_number]}')

else:
    firm_bundle_number = 1337
    utils.print_and_log('[VERBOSE] Device is not A9, continuing...', is_verbose)

if args.update:
    if not args.restore:
        utils.print_and_log('[ERROR] Update argument specified without restore argument!\nExiting...', is_verbose)

if args.create:
    if args.restore:
        ipsw_path = create_ipsw()
    create_ipsw()
    fresh_ipsw = True
else:
    ipsw_path = args.ipsw[0]
    fresh_ipsw = False

if args.restore:
    restore(fresh_ipsw, ipsw_path)