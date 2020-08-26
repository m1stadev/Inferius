import os
import shutil
import json
import sys
import zipfile
import requests
from remotezip import RemoteZip
import glob
import hashlib

def a9_check(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
    if 'devices' in data:
        return True
    else:
        return False

def fetch_a9_boardconfigs(firm_bundle):
    board_configs = []
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
    for x in range(0, len(data['devices'])):
        board_configs.append(data['devices'][x]['boardconfig'])
    return board_configs

def extract_ipsw(ipsw, verbose=None):
    os.makedirs('work/ipsw', exist_ok = True)
    if not os.path.exists(ipsw):
        sys.exit(f"IPSW at '{ipsw}' doesn't exist!\nExiting...")
    if zipfile.is_zipfile(ipsw):
        pass
        if verbose:
            print(f'[VERBOSE] {ipsw} is a zip archive!')
    else:
        sys.exit(f'{ipsw} is not a valid IPSW!\nExiting...')
    if ipsw.endswith('.ipsw'):
        if verbose:
            print(f'Extracting IPSW at {ipsw}. This may take a while, please wait...')
        else:
            print('Extracting IPSW. This may take a while, please wait...')
        with zipfile.ZipFile(ipsw, 'r') as ipsw:
            ipsw.extractall('work/ipsw')
    if verbose:
        print(f'[VERBOSE] IPSW extracted to: work/ipsw')
    return 'work/ipsw'
    
def find_bundle(device_identifier, version, verbose=None):
    if os.path.isdir(f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'):
        if verbose:
            print(f'[VERBOSE] Firmware bundle exists at: resources/FirmwareBundles/{device_identifier}_{version}_bundle')
        return f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'
    else:
        sys.exit(f"Firmware bundle for {device_identifier}, {version} doesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named {device_identifier}_{version}_bundle")

def grab_latest_llb_iboot(device_identifier, ipsw_dir, firm_bundle, firm_bundle_number):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        if firm_bundle_number != 1337:
            hardware_model = data['devices'][firm_bundle_number]['boardconfig']
        else:
            hardware_model = data['boardconfig']
    ipswme_device_info = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    device_info = ipswme_device_info.json()
    for x in range(0, len(device_info['firmwares'])):
        if device_info['firmwares'][x]['signed'] == True:
            ipsw_download = device_info['firmwares'][x]['url']
    with RemoteZip(ipsw_download) as ipsw:
        ipsw.extract(f'Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p')
        ipsw.extract(f'Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p')
    shutil.copy(f'Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p', f'{ipsw_dir}/Firmware/all_flash/')
    shutil.copy(f'Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p', f'{ipsw_dir}/Firmware/all_flash/')
    shutil.rmtree('Firmware')

def verify_bootchain(firm_bundle, firm_bundle_number, verbose=None):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        if firm_bundle_number == 1337:
            bootchain_path = [data['files']['ibss']['file'], data['files']['ibec']['file'], data['files']['ramdisk']['file'], data['files']['kernelcache']['file']]
            bootchain_sha1 = [data['files']['ibss']['sha1'], data['files']['ibec']['sha1'], data['files']['ramdisk']['sha1'], data['files']['kernelcache']['sha1']]
        else:
            bootchain_path = [data['devices'][firm_bundle_number]['files']['ibss']['file'], data['devices'][firm_bundle_number]['files']['ibec']['file'], data['ramdisk']['file'], data['kernelcache']['file']]
            bootchain_sha1 = [data['devices'][firm_bundle_number]['files']['ibss']['sha1'], data['devices'][firm_bundle_number]['files']['ibec']['sha1'], data['ramdisk']['sha1'], data['kernelcache']['sha1']]

    for x in range(0, len(bootchain_path)):
        with open(f'work/ipsw/{bootchain_path[x]}', 'rb') as f:
            # read contents of the file
            file_data = f.read()    
            sha1_hash = str(hashlib.sha1(file_data).hexdigest())
        if sha1_hash == bootchain_sha1[x]:
            if verbose:
                print(f'[VERBOSE] {bootchain_path[x]} verified!')
        else:
            sys.exit(f'work/ipsw/{bootchain_path[x]} is not verified! Redownload your IPSW, and try again.\nExiting...')

def extract_ibss_ibec(ipsw, firm_bundle, firm_bundle_number, verbose=None):
    if os.path.isfile(ipsw):
        pass
    else:
        sys.exit(f'IPSW {ipsw} does not exist!\nExiting...')
    if zipfile.is_zipfile(ipsw):
        pass
        if verbose:
            print(f'[VERBOSE] {ipsw} is a zip archive!')
    else:
        sys.exit(f'IPSW {ipsw} is not a valid IPSW!\nExiting...')
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        if firm_bundle_number == 1337:
            ibss_path = data['files']['ibss']['file']
            ibec_path = data['files']['ibec']['file']
        else:
            ibss_path = data['devices'][firm_bundle_number]['files']['ibss']['file']
            ibec_path = data['devices'][firm_bundle_number]['files']['ibec']['file']
    with zipfile.ZipFile(ipsw, 'r') as ipsw:
        ipsw.extract(ibss_path, path='work/ipsw')
        if verbose:
            print(f'[VERBOSE] Extracted {ibss_path} from IPSW to work/ipsw/')
        ipsw.extract(ibec_path, path='work/ipsw')
        if verbose:
            print(f'[VERBOSE] Extracted {ibec_path} from IPSW to work/ipsw/')
        ipsw.close()
    return ibss_path, ibec_path

def fetch_processor(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        return data['processor']

def make_ipsw(ipsw_dir, firm_bundle, verbose=None):
    if os.path.isfile(f'{firm_bundle[26:-7]}_custom.ipsw'):
        if verbose:
            print(f'[VERBOSE] Found custom IPSW from previous run: {firm_bundle[26:-7]}_custom.ipsw, deleting...')
        os.remove(f'{firm_bundle[26:-7]}_custom.ipsw')
    shutil.make_archive(f'{firm_bundle[26:-7]}', 'zip', ipsw_dir)
    os.rename(f'{firm_bundle[26:-7]}.zip', f'{firm_bundle[26:-7]}_custom.ipsw')
    return f'{firm_bundle[26:-7]}_custom.ipsw'
