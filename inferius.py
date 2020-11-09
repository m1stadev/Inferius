#!/usr/bin/env python3

from resources import ipsw, patch, restore, utils
import argparse
import atexit
import os
import platform
import subprocess
import sys

atexit.register(utils.cleanup)
utils.cleanup(True)

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
    utils.log('Verifying IPSW. This may take a while, please wait...', True)
    is_stock = ipsw.verify_ipsw(device_identifier, args.version[0], args.ipsw[0], buildid, is_verbose)
    if not is_stock:
        sys.exit(f'[ERROR] IPSW {args.ipsw[0]} is not verified! Redownload your IPSW, and try again.\nExiting...')

    utils.log('IPSW verified! Extracting IPSW...', True)
    ipsw.extract_ipsw(args.ipsw[0], is_verbose)

    utils.log('IPSW extracted! Patching bootchain...', True)
    patch.patch_bootchain(firmware_bundle, firm_bundle_number, buildid, is_verbose)

    utils.log('Bootchain patched! Grabbing latest LLB and iBoot to put into custom IPSW...', True)
    ipsw.grab_latest_llb_iboot(device_identifier, args.version[0], firmware_bundle, firm_bundle_number, is_verbose)

    utils.log('Packing everything into custom IPSW. This may take a while, please wait...', True)
    ipsw_name = ipsw.make_ipsw(firmware_bundle, is_verbose)

    utils.log(f'Done!\nCustom IPSW at: {ipsw_name}', True)

    if not args.restore:
        utils.cleanup(True)

    return ipsw_name

def restore_ipsw(fresh_ipsw, ipsw_path):
    processor = ipsw.fetch_processor(firmware_bundle)

    if fresh_ipsw:
        utils.log('------------RESTORE-BEGINNING------------', False)
        utils.log('Restoring freshly created custom IPSW', is_verbose)
    else:
        utils.log('Inferius Restore Log', False)
        utils.log('Checking if IPSW is custom...', False)
        is_stock = ipsw.verify_ipsw(device_identifier, args.version[0], ipsw_path, buildid, is_verbose)
        if is_stock:
            utils.log('[ERROR] IPSW is stock!\nExiting...', False)
            sys.exit()

    if args.update:
        keep_data = True
    else:
        keep_data = False

    device_check = input('Is your device is connected in Pwned DFU mode with signature checks removed? [Y/N]: ')
    utils.log(f'Is your device is connected in Pwned DFU mode with signature checks removed? [Y/N]: {device_check}', False)

    if not 'y' in device_check.lower():
        utils.log('[ERROR] Specified device is not in pwndfu!\nExiting...', is_verbose)
        sys.exit()

    lsusb = subprocess.run('./resources/bin/lsusb', stdout=subprocess.PIPE, universal_newlines=True)
    utils.log(lsusb.stdout, False)

    if not 'Apple Mobile Device (DFU Mode)' in lsusb.stdout:
        utils.log('[ERROR] Specified device is not in pwndfu!\nExiting...', is_verbose)
        sys.exit()

    os.makedirs('work/ipsw', exist_ok=True)
    utils.log('Fetching some required info...', True)
    restore.save_blobs(device_identifier, firm_bundle_number, board_configs, downgrade_10, is_verbose)

    utils.log('Extracting iBSS and iBEC from custom IPSW...', True)
    ibss_path, ibec_path = ipsw.extract_bootchain(ipsw_path, firmware_bundle, firm_bundle_number, is_verbose)

    utils.log('Signing iBSS and iBEC with SHSH blob...', True)
    restore.sign_bootchain(ibss_path, ibec_path, is_verbose)

    utils.log('Preparations done! Beginning restore...', True)
    if downgrade_10:
        ipsw.fetch_1033_sepbb(device_identifier, args.version[0], is_verbose)

    restore.send_bootchain(processor, is_verbose)
    futurerestore = restore.restore(ipsw_path, ipsw.is_cellular(device_identifier), keep_data, downgrade_10, is_verbose)
    if not futurerestore:
        sys.exit()
    else:
        utils.cleanup(True)

    utils.log('Done.\nExiting...', True)

if not args.ipsw:
    sys.exit(parser.print_help(sys.stderr))

if args.device:
    utils.log('Inferius Log', False)
    device_identifier = args.device[0].lower()
    device_identifier = device_identifier.replace('p', 'P')
    utils.log(f'[INFO] Device: {device_identifier}', False)
else:
    sys.exit(parser.print_help(sys.stderr))

if args.verbose:
    is_verbose = True
else:
    is_verbose = False

if args.version:
    version_str = args.version[0]
    version_str = version_str.split('.')
    unsupported_major_versions = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '14']

    if version_str[0] in unsupported_major_versions:
        sys.exit(f'[ERROR] iOS {version_str[0]}.x downgrades are not currently supported!\nExiting...')    
    elif version_str[0] == '10':
        if not ipsw.is_a7(device_identifier):
            utils.log('[ERROR] Only A7 devices can downgrade to iOS 10.x currently!\nExiting...', True)
            sys.exit()
        downgrade_10 = True
        ipsw.fetch_1033_ota_bm(device_identifier, args.version[0])
    else:
        downgrade_10 = False

    if args.version[0] == '10.1.1' or args.version[0] == '12.1.2':
        ipsw.fetch_ipsw_bm(args.ipsw[0], is_verbose) 

else:
    sys.exit(parser.print_help(sys.stderr))

utils.log(f'[VERBOSE] Verifying device {device_identifier} exists...', is_verbose)
ipsw.verify_device(device_identifier, is_verbose)
utils.log(f'[VERBOSE] Verifying iOS {args.version[0]} exists for device {device_identifier}...', is_verbose)
ipsw.verify_version(device_identifier, args.version[0], is_verbose)
utils.log(f'[INFO] iOS Version: {args.version[0]}', False)

if not utils.check_internet():
    sys.exit('[ERROR] You are not connected to the Internet. Connect to the internet, then run this script again.\nExiting...')

utils.log(f'[VERBOSE] Finding Firmware Bundle for {device_identifier}, {args.version[0]}', is_verbose)
firmware_bundle = ipsw.find_bundle(device_identifier, args.version[0], is_verbose)

if args.version[0] == '10.1.1' or args.version[0] == '12.1.2':
    utils.log(f'[VERBOSE] Finding proper buildid for version {args.version[0]}', is_verbose)
    buildid = ipsw.check_buildid(firmware_bundle) 
else:
    buildid = False

utils.log('[VERBOSE] Checking if device is A9...', is_verbose)
if ipsw.is_a9(firmware_bundle):
    utils.log('[VERBOSE] Device is A9, fetching correct board config...', is_verbose)

    board_configs = ipsw.fetch_boardconfig(firmware_bundle)
    if len(board_configs) != 2:
        utils.log('[ERROR] Firmware Bundle is invalid.\nExiting...', True)
        sys.exit()

    firm_bundle_number = input(f'A9 device detected, please choose the number of the correct board config for your device:\n  [1] {board_configs[0]}ap\n  [2] {board_configs[1]}ap\nChoice: ')
    utils.log(f'A9 device detected, please choose the number of the correct board config for your device:\n  [1] {board_configs[0]}ap\n  [2] {board_configs[1]}ap\nChoice: {firm_bundle_number}', False)

    try:
        int(firm_bundle_number)
    except ValueError:
        utils.log('[Error] Input not a number!\nExiting...', True)
        sys.exit()
    
    utils.log(f'[INFO] Firmware bundle number: {firm_bundle_number}', False)
    firm_bundle_number = int(firm_bundle_number)
    if 0 < firm_bundle_number < 3:
        firm_bundle_number = firm_bundle_number - 1
    else:
        utils.log('[ERROR] Invalid input given.\nExiting...', True)
        sys.exit()

    utils.log(f'[INFO] Device boardconfig: {board_configs[firm_bundle_number]}', False)

else:
    board_configs = None
    firm_bundle_number = 1337
    utils.log('[VERBOSE] Device is not A9, continuing...', is_verbose)

if args.update:
    if not args.restore:
        utils.log('[ERROR] Update argument specified without restore argument!\nExiting...', is_verbose)

if args.create:
    fresh_ipsw = True
    if args.restore:
        ipsw_path = create_ipsw()
    else:
        create_ipsw()
else:
    fresh_ipsw = False
    ipsw_path = args.ipsw[0]

if args.restore:
    restore_ipsw(fresh_ipsw, ipsw_path)