import json
import os
import subprocess
import time
import sys
from . import log

def send_bootchain(processor, verbose=None):

    if processor.lower() == 's5l8960' or processor.lower() == 't8015':
        subprocess.run('./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)

    ibss_send = subprocess.run('./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if verbose:
        print(ibss_send.stdout)


    ibec_send = subprocess.run('./resources/bin/irecovery -f work/ipsw/ibec.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if verbose:
        print(ibec_send.stdout)

    if processor.lower() == 't8010' or processor.lower() == 't8015':
        subprocess.run('./resources/bin/irecovery -c go', stdout=subprocess.PIPE, universal_newlines=True, shell=True)

    if verbose:
        print('[VERBOSE] Checking if device is in pwnrecovery...')

    recmode_check = subprocess.run('./resources/bin/lsusb', stdout=subprocess.PIPE, universal_newlines=True, shell=True)

    if 'Apple Mobile Device (Recovery Mode)' in recmode_check.stdout:

        if verbose:

            print('[VERBOSE] Device entered pwnrecovery successfully!')
            log.log_to_file('[VERBOSE] Device entered pwnrecovery successfully!')

    else:
        sys.exit('Device did not enter recovery mode successfully! Make sure your device is in Pwned DFU mode with signature checks removed, then run this script again.\nExiting...')

def is_cellular(device_identifier):
    non_cellular_devices = ['ipad6,11', 'ipad7,5', 'ipad7,11', 'ipod7,1', 'ipod9,1', 'ipad4,1', 'ipad5,3', 'ipad6,7', 'ipad6,3', 'ipad7,1', 'ipad7,3', 'ipad4,4', 'ipad4,7', 'ipad5,1']
    device_identifier = device_identifier.lower()

    if device_identifier in non_cellular_devices:
        is_cellular = True

    else:
        is_cellular = False

    return is_cellular

def restore(ipsw_path, is_cellular, keep_data, verbose=None):
    if is_cellular:
        
        if verbose:
            print('[VERBOSE] Device has cellular support, continuing with restore.')
            log.log_to_file('[VERBOSE] Device has cellular support, continuing with restore.')

        if keep_data:
            print('Update option enabled, saving data.')
            update = ' -u '
        else:
            update = ' '
        
        futurerestore = subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2{update}--latest-sep --latest-baseband {ipsw_path}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        log.log_to_file(futurerestore.stdout)

    else:
        if keep_data:
            print('Update option enabled, saving data.')
            update = ' -u '
        else:
            update = ' '
        
        futurerestore = subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2{update}--latest-sep --no-baseband {ipsw_path}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        log.log_to_file(futurerestore.stdout)