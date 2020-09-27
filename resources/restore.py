from . import ipsw, utils
import glob
import json
import os
import subprocess
import sys
import time

def send_bootchain(processor, is_verbose):
    if processor.lower() == 's5l8960' or processor.lower() == 't8015':
        subprocess.run('./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True) # A7/A11 need to reset their usb connection, this does the job

    ibss_send = subprocess.run('./resources/bin/irecovery -f work/ipsw/ibss.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(ibss_send.stdout, False)
    utils.log('[VERBOSE] Sent iBSS', is_verbose)

    ibec_send = subprocess.run('./resources/bin/irecovery -f work/ipsw/ibec.img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(ibec_send.stdout, False)
    utils.log('[VERBOSE] Sent iBEC', is_verbose)

    if processor.lower() == 't8010' or processor.lower() == 't8015': # A10/A11 needs to boot iBEC after sending
        subprocess.run('./resources/bin/irecovery -c go', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        utils.log('[VERBOSE] Booted iBEC', is_verbose)
        
    time.sleep(3)
    utils.log('[VERBOSE] Checking if device is in pwnrecovery...', is_verbose)
    recmode_check = subprocess.run('./resources/bin/lsusb', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if 'Apple Mobile Device (Recovery Mode)' in recmode_check.stdout:
        utils.log('[VERBOSE] Device entered pwnrecovery successfully!', is_verbose)

    else:
        utils.log('[ERROR] Device did not enter recovery mode successfully! Make sure your device is in Pwned DFU mode with signature checks removed, then run this script again.\nExiting...', True)
        sys.exit()

def restore(ipsw_path, is_cellular, keep_data, downgrade_10, is_verbose):
    if keep_data:
        utils.log('[VERBOSE] Requested to update instead of erase, saving data...', is_verbose)
        update = ' -u '
    else:
        update = ' '
    
    if downgrade_10:
        utils.log('[VERBOSE] Downgrading to iOS 10 using 10.3.3 SEP...', is_verbose)
        sep_fw = '-s work/tmp/1033_SEPBB/sep-firmware.im4p -m work/OTA_BuildManifest.plist'
    else:
        sep_fw = '--latest-sep'

    if is_cellular:
        utils.log('[VERBOSE] Device has cellular support, restoring with baseband.', is_verbose)
        if downgrade_10:
            baseband = '-b work/tmp/1033_SEPBB/baseband.bbfw -p work/OTA_BuildManifest.plist'
        else:
            baseband = '--latest-baseband'

    else:
        baseband = '--no-baseband'

    futurerestore = subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2{update}{sep_fw} {baseband} {ipsw_path}', stdout=sys.stdout, universal_newlines=True, shell=True)

    if futurerestore.stdout != 0:
        utils.log('[ERROR] Restore failed!\nExiting...', True)
        return False
    else:
        utils.log('Restore successful!\nCleaning up...', True)
        return True

def save_blobs(device_identifier, firm_bundle_number, board_configs, downgrade_10, is_verbose):
    if downgrade_10:
        blob_version = '-i 9.9.10.3.3 -o -m work/OTA_BuildManifest.plist'
        if not os.path.isfile('work/OTA_BuildManifest.plist'):
            utils.log('[ERROR] OTA BuildManifest does not exist!\nExiting...', True)
            sys.exit()
    else:
        blob_version = '-l'

    utils.log('[VERBOSE] Fetching ECID...', is_verbose)
    fetch_ecid = subprocess.run('./resources/bin/igetnonce | grep ECID', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(fetch_ecid.stdout, False)
    ecid = fetch_ecid.stdout[5:-1]
    utils.log(f'[VERBOSE] ECID: 0x{ecid}', is_verbose)

    utils.log('[VERBOSE] Fetching apnonce...', is_verbose)
    fetch_apnonce = subprocess.run('./resources/bin/igetnonce | grep ApNonce', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(fetch_apnonce.stdout, False)
    apnonce = fetch_apnonce.stdout[8:-1]
    utils.log(f'[VERBOSE] apnonce: {apnonce}', is_verbose)

    if board_configs:
        fetch_blobs = subprocess.run(f'./resources/bin/tsschecker -d {device_identifier} {blob_version} -B {board_configs[firm_bundle_number]}ap -e 0x{ecid} -s --apnonce {apnonce} --save-path work/ipsw', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    else:
        fetch_blobs = subprocess.run(f'./resources/bin/tsschecker -d {device_identifier} {blob_version} -e 0x{ecid} -s --apnonce {apnonce} --save-path work/ipsw', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(fetch_blobs.stdout, False)
    
    if not 'Saved shsh blobs!' in fetch_blobs.stdout:
        utils.log("[ERROR] SHSH didn't save! Make sure you're connected to the internet, then try again.\nExiting...", True)
        sys.exit()

    for shsh in glob.glob('work/ipsw/*.shsh*'):
        os.rename(shsh, 'work/ipsw/blob.shsh2')

    if ipsw.is_a7(device_identifier):
        fetch_blobs = subprocess.run(f'./resources/bin/tsschecker -d {device_identifier} {blob_version} -e 0x{ecid} -s --save-path work/ipsw', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        utils.log(fetch_blobs.stdout, False)

        for shsh in glob.glob('work/ipsw/*.shsh2'):
            if shsh == 'work/ipsw/blob.shsh2':
                continue
            os.rename(shsh, 'work/ipsw/signing_blob.shsh2')

    utils.log('SHSH blobs saved!', True)

def sign_bootchain(ibss_path, ibec_path, is_verbose):
    if os.path.isfile('work/ipsw/signing_blob.shsh2'):
        shsh_path = 'work/ipsw/signing_blob.shsh2'
    else:
        shsh_path = 'work/ipsw/blob.shsh2'

    print(f'SHSH PATH: {shsh_path}')
    sign_ibss = subprocess.run(f'./resources/bin/img4tool -c work/ipsw/ibss.img4 -p {ibss_path} -s {shsh_path}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(sign_ibss.stdout, False)
    if 'img4tool: failed' in sign_ibss.stdout:
        utils.log('[ERROR] iBSS failed to be signed!\nExiting...', is_verbose)
        sys.exit()

    utils.log('[VERBOSE] iBSS packed into img4', is_verbose)

    sign_ibec = subprocess.run(f'./resources/bin/img4tool -c work/ipsw/ibec.img4 -p {ibec_path} -s {shsh_path}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.log(sign_ibec.stdout, False)
    if 'img4tool: failed' in sign_ibec.stdout:
        utils.log('[ERROR] iBEC failed to be signed!\nExiting...', is_verbose)
        sys.exit()
    
    utils.log('[VERBOSE] iBEC packed into img4', is_verbose)