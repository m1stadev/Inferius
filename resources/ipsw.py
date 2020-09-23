from . import utils
from remotezip import RemoteZip
from urllib.request import urlopen
import glob
import hashlib
import json
import os
import requests
import shutil
import sys
import zipfile

def is_a9(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    if 'devices' in data:
        is_a9 = True
    else:
        is_a9 = False
    return is_a9

def fetch_boardconfig(firm_bundle):
    board_configs = []

    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    for x in range(0, len(data['devices'])):
        board_configs.append(data['devices'][x]['boardconfig'])

    return board_configs

def extract_ipsw(ipsw, is_verbose):
    if not os.path.exists(ipsw):
        sys.exit(f"[ERROR] IPSW at '{ipsw}' doesn't exist!\nExiting...")

    if zipfile.is_zipfile(ipsw):
        pass
    else:
        sys.exit(f'[ERROR] {ipsw} is not a valid IPSW!\nExiting...')

    utils.print_and_log(f'[VERBOSE] {ipsw} is a zip archive!', is_verbose)
    if ipsw.endswith('.ipsw'):
        pass
    else:
        utils.print_and_log(f'[Warning] IPSW {ipsw} does not have .ipsw extension! Continuing...', is_verbose)
        
    utils.print_and_log('[VERBOSE] Extracting IPSW. This may take a while, please wait...', is_verbose)
    with zipfile.ZipFile(ipsw, 'r') as ipsw:
        try:
            ipsw.extractall('work/ipsw')
        except OSError:
            utils.print_and_log('[ERROR] Ran out of storage while extracting IPSW. Clear up some space on your computer, then run this script again.\nExiting...', is_verbose)
            sys.exit()

        utils.print_and_log('[VERBOSE] IPSW extracted to: work/ipsw', is_verbose)
        
def find_bundle(device_identifier, version, is_verbose):
    if os.path.isdir(f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'):
        pass
    else:
        sys.exit(f"[ERROR] Firmware bundle for {device_identifier}, {version} doesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named '{device_identifier}_{version}_bundle'")

    utils.print_and_log(f'[VERBOSE] Firmware bundle exists at: resources/FirmwareBundles/{device_identifier}_{version}_bundle', is_verbose)
    return f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'


def grab_latest_llb_iboot(device_identifier, firm_bundle, firm_bundle_number):
    ipswme_device_info = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    device_info = ipswme_device_info.json()
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        if firm_bundle_number != 1337:
            hardware_model = data['devices'][firm_bundle_number]['boardconfig']
        else:
            hardware_model = data['boardconfig']

    for x in range(0, len(device_info['firmwares'])):
        if device_info['firmwares'][x]['signed'] == True:
            ipsw_download = device_info['firmwares'][x]['url']

    with RemoteZip(ipsw_download) as ipsw:
        os.makedirs('work/tmp')
        os.chdir('work/tmp/')
        ipsw.extract(f'Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p')
        ipsw.extract(f'Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p')
        os.chdir('../../')

    shutil.copy(f'work/tmp/Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p', 'work/ipsw/Firmware/all_flash/')
    shutil.copy(f'work/tmp/Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p', 'work/ipsw/Firmware/all_flash/')

    shutil.rmtree('work/tmp')

def verify_bootchain(firm_bundle, firm_bundle_number, is_verbose):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    if firm_bundle_number == 1337:
        bootchain_path = [data['files']['ibss']['file'], data['files']['ibec']['file'], data['files']['ramdisk']['file'], data['files']['kernelcache']['file']]
        bootchain_sha1 = [data['files']['ibss']['sha1'], data['files']['ibec']['sha1'], data['files']['ramdisk']['sha1'], data['files']['kernelcache']['sha1']]
    else:
        bootchain_path = [data['devices'][firm_bundle_number]['files']['ibss']['file'], data['devices'][firm_bundle_number]['files']['ibec']['file'], data['files']['ramdisk']['file'], data['files']['kernelcache']['file']]
        bootchain_sha1 = [data['devices'][firm_bundle_number]['files']['ibss']['sha1'], data['devices'][firm_bundle_number]['files']['ibec']['sha1'], data['files']['ramdisk']['sha1'], data['files']['kernelcache']['sha1']]

    for x in range(0, len(bootchain_path)):
        with open(f'work/ipsw/{bootchain_path[x]}', 'rb') as f:
            sha1_hash = str(hashlib.sha1(f.read()).hexdigest())

        if sha1_hash == bootchain_sha1[x]:
            utils.print_and_log(f'[VERBOSE] {bootchain_path[x]} verified!', is_verbose)
        else:
            utils.print_and_log(f'[ERROR] work/ipsw/{bootchain_path[x]} is not verified! Redownload your IPSW, and try again.\nExiting...', True)
            sys.exit()

def extract_ibss_ibec(ipsw, firm_bundle, firm_bundle_number, is_verbose):
    if os.path.isfile(ipsw):
        pass
    else:
        utils.print_and_log(f'IPSW {ipsw} does not exist!\nExiting...', is_verbose)
        sys.exit()

    if not zipfile.is_zipfile(ipsw):
        utils.print_and_log(f'[ERROR] IPSW {ipsw} is not a valid IPSW!\nExiting...', True)
        sys.exit()
    utils.print_and_log(f'[VERBOSE] {ipsw} is a valid zip archive!', is_verbose)

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
        utils.print_and_log(f'[VERBOSE] Extracted {ibss_path} from IPSW to work/ipsw/', is_verbose)

        ipsw.extract(ibec_path, path='work/ipsw')
        utils.print_and_log(f'[VERBOSE] Extracted {ibec_path} from IPSW to work/ipsw/', is_verbose)

    return ibss_path, ibec_path

def fetch_processor(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    return data['processor']

def make_ipsw(firm_bundle, is_verbose):
    if os.path.isfile(f'{firm_bundle[26:-7]}_custom.ipsw'):
        utils.print_and_log('[VERBOSE] Found custom IPSW from previous run, deleting...', is_verbose)
        os.remove(f'{firm_bundle[26:-7]}_custom.ipsw')

    try:
        shutil.make_archive(f'work/{firm_bundle[26:-7]}', 'zip', 'work/ipsw')
    except OSError:
        utils.print_and_log('[ERROR] No more space available to create IPSW. Clear up some space on your computer, then run this script again.', True)
        sys.exit()

    os.makedirs('created_ipsws', exist_ok=True)
    os.rename(f'work/{firm_bundle[26:-7]}.zip', f'created_ipsws/{firm_bundle[26:-7]}_custom.ipsw')
    return f'created_ipsws/{firm_bundle[26:-7]}_custom.ipsw'

def verify_ipsw(device_identifier, version, ipsw_dir, is_verbose):
    api_data = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    data = api_data.json()

    for x in range(0, len(data['firmwares'])):
        if data['firmwares'][x]['version'] == version:
            ipsw_sha1 = data['firmwares'][x]['sha1sum']
            break

    with open(ipsw_dir, 'rb') as f:
        sha1 = hashlib.sha1()
        file_buffer = f.read(8192)
        while len(file_buffer) > 0:
            sha1.update(file_buffer)
            file_buffer = f.read(8192)
        
    if ipsw_sha1 == sha1.hexdigest():
        utils.print_and_log(f'[VERBOSE] IPSW {ipsw_dir} verified!', is_verbose)
        return True
    else:
        return False

def verify_version(device_identifier, version, is_verbose):
    api_data = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    data = api_data.json()
    device_identifier.replace('p', 'P')
    try:
        float(version)
    except ValueError:
        utils.print_and_log(f'[ERROR] {version} is not a valid iOS version!\nExiting...', is_verbose)
        sys.exit()

    for x in range(0, len(data['firmwares'])):
        if data['firmwares'][x]['version'] == version:
            valid_version = True
            break
        else:
            valid_version = False
    
    if not valid_version:
        utils.print_and_log(f'[ERROR] iOS {version} does not exist for device {device_identifier}!\nExiting...', is_verbose)
        sys.exit()

    utils.print_and_log(f'[VERBOSE] iOS {version} exists for device {device_identifier}!', is_verbose)

def verify_device(device_identifier, is_verbose):
    api_data = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed')
    data = api_data.json()

    for x in data['devices']:
        if data['devices'][x] == data['devices'][device_identifier]:
            valid_device = True
            break
        else:
            valid_device = False
    
    if not valid_device:
        utils.print_and_log(f'[ERROR] Device {device_identifier} does not exist!\nExiting...', is_verbose)
        sys.exit()

    utils.print_and_log(f'[VERBOSE] Device {device_identifier} exists!', is_verbose)