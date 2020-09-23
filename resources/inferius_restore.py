from . import utils
import json
import os
import subprocess
import sys
import time

def send_bootchain(processor, is_verbose):
    if processor.lower() == 's5l8960' or processor.lower() == 't8015':
        subprocess.run('./resources/bin/irecovery -f nothing', stdout=subprocess.PIPE, universal_newlines=True, shell=True) # A7/A11 need to reset their usb connection, this does the job

    ibss_send = subprocess.run('./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(ibss_send.stdout)

    ibec_send = subprocess.run('./resources/bin/irecovery -f work/ipsw/ibec.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(ibec_send.stdout)

    if processor.lower() == 't8010' or processor.lower() == 't8015': # A10/A11 needs to boot iBEC after sending
        subprocess.run('./resources/bin/irecovery -c go', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    time.sleep(3)
    utils.print_and_log('[VERBOSE] Checking if device is in pwnrecovery...', is_verbose)
    recmode_check = subprocess.run('./resources/bin/lsusb', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if 'Apple Mobile Device (Recovery Mode)' in recmode_check.stdout:
        utils.print_and_log('[VERBOSE] Device entered pwnrecovery successfully!', is_verbose)
    else:
        utils.print_and_log('[ERROR] Device did not enter recovery mode successfully! Make sure your device is in Pwned DFU mode with signature checks removed, then run this script again.\nExiting...', True)
        sys.exit()

def is_cellular(device_identifier):
    non_cellular_devices = ['ipad6,11', 'ipad7,5', 'ipad7,11', 'ipod7,1', 'ipod9,1', 'ipad4,1', 'ipad5,3', 'ipad6,7', 'ipad6,3', 'ipad7,1', 'ipad7,3', 'ipad4,4', 'ipad4,7', 'ipad5,1']
    device_identifier = device_identifier.lower()

    if device_identifier in non_cellular_devices:
        is_cellular = False
    else:
        is_cellular = True

    return is_cellular

def restore(ipsw_path, is_cellular, keep_data, is_verbose):
    if keep_data:
        utils.print_and_log('[VERBOSE] Requested to update instead of erase, saving data...', is_verbose)
        update = ' -u '
    else:
        update = ' '
    if is_cellular:
        if is_verbose:
            utils.print_and_log('[VERBOSE] Device has cellular support, restoring with latest baseband.', is_verbose)

        futurerestore = subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2{update}--latest-sep --latest-baseband {ipsw_path}', stdout=sys.stdout, universal_newlines=True, shell=True)

    else: 
        futurerestore = subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2{update}--latest-sep --no-baseband {ipsw_path}', stdout=sys.stdout, universal_newlines=True, shell=True)
    utils.log(futurerestore.stdout)