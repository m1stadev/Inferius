import os
import shutil
import json
import sys
import zipfile
import requests
from remotezip import RemoteZip
import glob

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
        print('Extracting IPSW. This may take a while, please wait...')
        with zipfile.ZipFile(ipsw, 'r') as zip_ref:
            zip_ref.extractall('work/ipsw')
    if verbose:
        print(f'[VERBOSE] IPSW extracted to: work/ipsw')
    return 'work/ipsw'
    
def find_bundle(device_identifier, version, verbose=None):
    if os.path.isdir(f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'):
        if verbose:
            print(f'[VERBOSE] Firmware bundle exists at: resources/FirmwareBundles/{device_identifier}_{version}_bundle')
        return f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'
    else:
        sys.exit(f"Firmware bundle for\nDevice: {device_identifier}\nVersion: {version}\ndoesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named {device_identifier}_{version}_bundle")

def grab_latest_llb_iboot(device_identifier, ipsw_dir, firm_bundle, verbose=None):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        hardware_model = data['boardconfig']
    if device_identifier.startswith('iPhone6'):
        hardware_model = 'iphone6'
    ipswme_device_info = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    device_info = ipswme_device_info.json()
    for x in range(0, len(device_info['firmwares'])):
        if device_info['firmwares'][x]['signed'] == True:
            ipsw_download = device_info['firmwares'][x]['url']
    with RemoteZip(ipsw_download) as zip:
        zip.extract(f'Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p')
        zip.extract(f'Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p')
    shutil.copy(f'Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p', f'{ipsw_dir}/Firmware/all_flash/')
    shutil.copy(f'Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p', f'{ipsw_dir}/Firmware/all_flash/')
    shutil.rmtree('Firmware')

def make_ipsw(ipsw_dir, firm_bundle, verbose=None):
    if os.path.isfile(f'{firm_bundle[26:-7]}_custom.ipsw'):
        if verbose:
            print(f'Found custom IPSW from previous run: {firm_bundle[26:-7]}_custom.ipsw, deleting...')
        os.remove(f'{firm_bundle[26:-7]}_custom.ipsw')
    shutil.make_archive(f'{firm_bundle[26:-7]}', 'zip', ipsw_dir)
    os.rename(f'{firm_bundle[26:-7]}.zip', f'{firm_bundle[26:-7]}_custom.ipsw')
    return f'{firm_bundle[26:-7]}_custom.ipsw'