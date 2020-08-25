import json
import os
import subprocess
import time
import sys

def send_ibss_ibec(processor, verbose=None):
    with open('work/empty_file', 'w') as f:
        f.close()
    if processor.lower() == 's5l8960':
        subprocess.Popen(f'./resources/bin/irecovery -f work/empty_file', stdout=subprocess.PIPE, shell=True)
        time.sleep(5)
    subprocess.Popen(f'./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    subprocess.Popen(f'./resources/bin/irecovery -f work/ipsw/ibec.img4', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    if processor.lower() == 't8010' or 't8015':
        subprocess.Popen(f'./resources/bin/irecovery -c go', stdout=subprocess.PIPE, shell=True)
        time.sleep(5)
    if verbose:
        print('[VERBOSE] Checking if device is in pwnrecovery...')
    lsusb = subprocess.Popen('./resources/bin/lsusb', stdout=subprocess.PIPE, shell=True)
    time.sleep(10)
    lsusb_output = str(lsusb.stdout.read())
    if 'Apple Mobile Device (Recovery Mode)' in lsusb_output:
        if verbose:
            print('[VERBOSE] Device entered pwnrecovery successfully!')
    else:
        sys.exit('Device did not enter recovery mode successfully! Make sure your device is in Pwned DFU mode with signature checks removed, then run this script again.\nExiting...')

def is_cellular(device_identifier):
    non_cellular_devices = ['ipad6,11', 'ipad7,5', 'ipad7,11', 'ipod7,1', 'ipod9,1', 'ipad4,1', 'ipad5,3', 'ipad6,7', 'ipad6,3', 'ipad7,1', 'ipad7,3', 'ipad4,4', 'ipad4,7', 'ipad5,1']
    device_identifier = device_identifier.lower()
    if device_identifier in non_cellular_devices:
        return False
    else:
        return True

def restore(ipsw_path, is_cellular, verbose=None):
    os.chdir('work/ipsw')
    if is_cellular:
        subprocess.run(f'../../resources/bin/futurerestore -t blob.shsh2 --latest-sep --latest-baseband {ipsw_path}', shell=True)
    else:
        subprocess.run(f'../../resources/bin/futurerestore -t blob.shsh2 --latest-sep --no-baseband {ipsw_path}', shell=True)