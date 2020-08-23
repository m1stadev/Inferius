import json
import os
import subprocess
import time
import sys

def send_ibss_ibec(verbose=None):
    subprocess.Popen(f'./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    subprocess.Popen(f'./resources/bin/irecovery -f work/ipsw/ibec.img4', stdout=subprocess.PIPE, shell=True)
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

def restore(ipsw_path, verbose=None):
    os.chdir('work/ipsw')
    subprocess.run(f'../../resources/bin/futurerestore -t blob.shsh2 --latest-sep --latest-baseband {ipsw_path}', shell=True) # TODO: Implement check for if device is cellular or not.