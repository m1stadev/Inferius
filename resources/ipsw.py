from . import utils
from remotezip import RemoteZip
from urllib.request import urlopen
import glob
import hashlib
import json
import os
import plistlib
import requests
import shutil
import sys
import zipfile
import traceback
from tqdm import tqdm

import pathlib

def is_a9(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    if 'devices' in data:
        is_a9 = True
    else:
        is_a9 = False
    return is_a9

def is_a7(device_identifier):
    a7_devices = ['iPhone6,1', 'iPhone6,2', 'iPad4,1', 'iPad4,2', 'iPad4,3', 'iPad4,4', 'iPad4,5', 'iPad4,6', 'iPad4,7', 'iPad4,8', 'iPad4,9']
    if device_identifier in a7_devices:
        is_a7 = True
    else:
        is_a7 = False
    return is_a7

def is_apfs(version, is_verbose):
    major_ios = version.split('.')
    if int(major_ios[0]) < 10:
        return False
    elif int(major_ios[0]) > 10:
        return True
    elif float(f'{major_ios[0]}.{major_ios[1]}') >= 10.3:
        return True
    else:
        return False

def is_cellular(device_identifier):
    non_cellular_devices = ['ipad6,11', 'ipad7,5', 'ipad7,11', 'ipod7,1', 'ipod9,1', 'ipad4,1', 'ipad5,3', 'ipad6,7', 'ipad6,3', 'ipad7,1', 'ipad7,3', 'ipad4,4', 'ipad4,7', 'ipad5,1']
    device_identifier = device_identifier.lower()

    if device_identifier in non_cellular_devices:
        is_cellular = False
    else:
        is_cellular = True

    return is_cellular

def fetch_boardconfig(firm_bundle):
    board_configs = []

    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    for x in range(0, len(data['devices'])):
        board_configs.append(data['devices'][x]['boardconfig'])

    return board_configs

def extract_ipsw(ipsw, is_verbose):
    if ipsw.endswith('.ipsw'):
        pass
    else:
        utils.log(f'[Warning] IPSW {ipsw} does not have .ipsw extension! Continuing...', is_verbose)
        
    utils.log('[VERBOSE] Extracting IPSW. This may take a while, please wait...', is_verbose)
    with zipfile.ZipFile(ipsw, 'r') as ipsw:
        try:
            ipsw.extractall('work/ipsw')
        except OSError:
            utils.log('[ERROR] Ran out of storage while extracting IPSW. Clear up some space on your computer, then run this script again.\nExiting...', is_verbose)
            sys.exit()

        utils.log('[VERBOSE] IPSW extracted to: work/ipsw', is_verbose)
        
    
def find_bundle(device_identifier, version, is_verbose):

    if (pathlib.Path("resources") / "FirmwareBundles" / f"{device_identifier}_{version}_bundle").is_dir():
        utils.log(f'[VERBOSE] Firmware bundle exists at: {(pathlib.Path("resources") / "FirmwareBundles" / f"{device_identifier}_{version}_bundle").absolute()}', is_verbose)
        return (pathlib.Path("resources") / "FirmwareBundles" / f"{device_identifier}_{version}_bundle").absolute()
    else:
        utils.log("[WARNING]: No Firmware bundle found, checking Github and downloading.", is_verbose=is_verbose)
        try:
            call_bundle_repo = requests.get("https://api.github.com/repos/marijuanARM/inferius-bundles/contents")
            if call_bundle_repo.status_code == requests.codes.ok:
                try:
                    parse_response = call_bundle_repo.json()
                except Exception:
                    utils.log("[ERROR]: Could Not parse API response from Github!", is_verbose=is_verbose)
                    sys.exit(f"[ERROR] Firmware bundle for {device_identifier}, {version} doesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named '{device_identifier}_{version}_bundle'")


                # Make sure the download file directory is ready to go.

                if not (pathlib.Path("resources") / "FirmwareBundles").is_dir():
                    if (pathlib.Path("resources") / "FirmwareBundles").is_file() or (pathlib.Path("resources") / "FirmwareBundles").exists():
                        sys.exit(f"[ERROR] Attempted to detect folder called FirmwareBundles but it appears a (non-folder) item already exists with the same name. Please delete the offending file and restart.")
                    (pathlib.Path("resources") / "FirmwareBundles").mkdir()

                


                target_file_name = f"{device_identifier}_{version}_bundle.zip"


                
                was_bundle_found = False
                for bundle_found in parse_response:
                    if bundle_found['name'] == target_file_name:
                        utils.log("[DEBUG]: Found Target Bundle Name! Downloading from Github.", is_verbose)
                        bundle_found_download_link = bundle_found['download_url']
                        _download_file_request = requests.get(bundle_found_download_link, stream=True)
                        total_size_for_download_request = int(
                            _download_file_request.headers.get("content-length", 0)
                        )

                        progress_bar = tqdm(total=total_size_for_download_request, unit="iB", unit_scale=True)
                        with open((pathlib.Path("resources") / "FirmwareBundles" / target_file_name), "wb") as file:
                            for data in _download_file_request.iter_content(chunk_size=1024):
                                progress_bar.update(len(data))
                                file.write(data)
                        progress_bar.close()

                        if total_size_for_download_request != 0 and progress_bar.n != total_size_for_download_request:
                            sys.exit(f"[INFO]: There was an issue with downloading the requested firmware bundle. Please download the required firmware bundle here: \n {bundle_found_download_link} ")
                        was_bundle_found = True

                        with zipfile.ZipFile((pathlib.Path("resources") / "FirmwareBundles" / target_file_name), 'r') as zipped_bundle:
                            try:
                                if (pathlib.Path("resources") / "FirmwareBundles" / f"{device_identifier}_{version}_bundle").is_dir() == True:
                                    sys.exit("[ERROR] Directory to extract to already exists. This shouldn't happen. Please open an issue on Github.")

                                (pathlib.Path("resources") / "FirmwareBundles" / f"{device_identifier}_{version}_bundle").mkdir()

                                zipped_bundle.extractall((pathlib.Path("resources") / "FirmwareBundles" / f"{device_identifier}_{version}_bundle"))
                            except OSError:
                                utils.log('[ERROR] Ran out of storage while extracting bundle. Clear up some space on your computer, then run this script again.\nExiting...', is_verbose)
                                sys.exit()
                            except Exception:
                                utils.log(f'[ERROR] Issue with extracted downloaded bundle. Please manually extract bundle located in {(pathlib.Path("resources") / "FirmwareBundles" / target_file_name).absolute()}\n to {(pathlib.Path("resources") / "FirmwareBundles").absolute()}\n and try again.', is_verbose)
                                
                                sys.exit(traceback.format_exc())
                        break
                
                if was_bundle_found == False:
                     sys.exit(f"[ERROR] Firmware bundle for {device_identifier}, {version} doesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in '{ (pathlib.Path('resources') / 'FirmwareBundles').absolute()  }'\nand named '{device_identifier}_{version}_bundle'")
                else:
                    return str((pathlib.Path("resources") / "FirmwareBundles" / target_file_name).absolute())

            else:
                utils.log(f"[ERROR]: Github has returned an error status code: {call_bundle_repo.status_code}", is_verbose)
                sys.exit(f"[ERROR] Firmware bundle for {device_identifier}, {version} doesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named '{device_identifier}_{version}_bundle'")
        except Exception:
            utils.log(f"[ERROR]: Unhandled exception attempting to grab from Github. {traceback.format_exc()}", is_verbose)
            
    sys.exit(f"[ERROR] Firmware bundle for {device_identifier}, {version} doesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named '{device_identifier}_{version}_bundle'")


def grab_latest_llb_iboot(device_identifier, version, firm_bundle, firm_bundle_number, is_verbose):
    is_ipsw_apfs = is_apfs(version, is_verbose)
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        if firm_bundle_number != 1337:
            hardware_model = data['devices'][firm_bundle_number]['boardconfig']
        else:
            hardware_model = data['boardconfig']

    ipswme_device_info = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    device_info = ipswme_device_info.json()
    for x in range(0, len(device_info['firmwares'])):
        if version.startswith('10.'):
            if device_info['firmwares'][x]['version'] == '10.3.3':
                ipsw_download = device_info['firmwares'][x]['url']
                utils.log(f'[VERBOSE] Found 10.3.3 IPSW to extract LLB and iBoot from\n[VERBOSE] URL: {ipsw_download}', is_verbose)

        elif device_info['firmwares'][x]['signed'] == True:
            ipsw_download = device_info['firmwares'][x]['url']
            utils.log(f'[VERBOSE] Found signed IPSW to extract LLB and iBoot from\n[VERBOSE] URL: {ipsw_download}', is_verbose)

    with RemoteZip(ipsw_download) as ipsw:
        os.makedirs('work/tmp/LLB_iBoot')
        os.chdir('work/tmp/LLB_iBoot')
        ipsw.extract(f'Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p')
        ipsw.extract(f'Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p')
        os.chdir('../../../')

    if is_ipsw_apfs:
        ipsw_dir = 'work/ipsw/Firmware/all_flash/'
        llb_file = f'LLB.{hardware_model}.RELEASE.im4p'
        iboot_file = f'iBoot.{hardware_model}.RELEASE.im4p'

    elif hardware_model == 'iphone6':
        full_boardconfig = device_info['boardconfig']
        semi_boardconfig = full_boardconfig[-2:]
        ipsw_dir = f'work/ipsw/Firmware/all_flash/all_flash.{full_boardconfig}.production/'
        llb_file = f'LLB.{semi_boardconfig}.RELEASE.im4p'
        iboot_file = f'iBoot.{semi_boardconfig}.RELEASE.im4p'

    else:
        ipsw_dir = f'work/ipsw/Firmware/all_flash/all_flash.{device_info["boardconfig"]}.production/'
        llb_file = f'LLB.{hardware_model}.RELEASE.im4p'
        iboot_file = f'iBoot.{semi_boardconfig}.RELEASE.im4p'

    os.rename(f'work/tmp/LLB_iBoot/Firmware/all_flash/LLB.{hardware_model}.RELEASE.im4p', f'{ipsw_dir + llb_file}')
    os.rename(f'work/tmp/LLB_iBoot/Firmware/all_flash/iBoot.{hardware_model}.RELEASE.im4p', f'{ipsw_dir + iboot_file}')
    shutil.rmtree('work/tmp/LLB_iBoot/')

def extract_bootchain(ipsw, firm_bundle, firm_bundle_number, is_verbose):
    if os.path.isfile(ipsw):
        pass
    else:
        utils.log(f'IPSW {ipsw} does not exist!\nExiting...', is_verbose)
        sys.exit()

    if not zipfile.is_zipfile(ipsw):
        utils.log(f'[ERROR] IPSW {ipsw} is not a valid IPSW!\nExiting...', True)
        sys.exit()
    utils.log(f'[VERBOSE] {ipsw} is a valid zip archive!', is_verbose)

    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

        if firm_bundle_number == 1337:
            ibss_path = data['files']['ibss']['file']
            ibec_path = data['files']['ibec']['file']
        else:
            ibss_path = data['devices'][firm_bundle_number]['files']['ibss']['file']
            ibec_path = data['devices'][firm_bundle_number]['files']['ibec']['file']

    with zipfile.ZipFile(ipsw, 'r') as ipsw:
        ipsw.extract(ibss_path, 'work/ipsw')
        utils.log(f'[VERBOSE] Extracted {ibss_path} from IPSW to work/ipsw', is_verbose)

        ipsw.extract(ibec_path, 'work/ipsw')
        utils.log(f'[VERBOSE] Extracted {ibec_path} from IPSW to work/ipsw', is_verbose)


    return f'work/ipsw/{ibss_path}', f'work/ipsw/{ibec_path}'

def fetch_processor(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    return data['processor']

def make_ipsw(firm_bundle, is_verbose):
    if os.path.isfile(f'created_ipsws/{firm_bundle[26:-7]}_custom.ipsw'):
        utils.log('[VERBOSE] Found custom IPSW from previous run, deleting...', is_verbose)
        os.remove(f'created_ipsws/{firm_bundle[26:-7]}_custom.ipsw')

    try:
        shutil.make_archive(f'work/{firm_bundle[26:-7]}', 'zip', 'work/ipsw')
    except OSError:
        utils.log('[ERROR] No more space available to create IPSW. Clear up some space on your computer, then run this script again.', True)
        sys.exit()

    os.makedirs('created_ipsws', exist_ok=True)

    os.rename(f'work/{firm_bundle[26:-7]}.zip', f'created_ipsws/{firm_bundle[26:-7]}_custom.ipsw')
    return f'created_ipsws/{firm_bundle[26:-7]}_custom.ipsw'

def verify_ipsw(device_identifier, version, ipsw_dir, buildid, is_verbose):
    api_data = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    data = api_data.json()

    for x in range(0, len(data['firmwares'])):
        if data['firmwares'][x]['version'] == version:
            if buildid:
                if data['firmwares'][x]['buildid'] == buildid:
                    ipsw_sha1 = data['firmwares'][x]['sha1sum']
                    break
            else:
                ipsw_sha1 = data['firmwares'][x]['sha1sum']
                break

    if not os.path.isfile(ipsw_dir):
        utils.log(f"[ERROR] IPSW {ipsw_dir} doesn't exist!\nExiting...", True)
        sys.exit()

    with open(ipsw_dir, 'rb') as f:
        sha1 = hashlib.sha1()
        file_buffer = f.read(8192)
        while len(file_buffer) > 0:
            sha1.update(file_buffer)
            file_buffer = f.read(8192)
        
    if ipsw_sha1 == sha1.hexdigest():
        utils.log(f'[VERBOSE] IPSW {ipsw_dir} verified!', is_verbose)
        return True
    else:
        return False

def verify_version(device_identifier, version, is_verbose):
    api_data = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    data = api_data.json()
    device_identifier.replace('p', 'P')

    for x in range(0, len(data['firmwares'])):
        if data['firmwares'][x]['version'] == version:
            valid_version = True
            break
        else:
            valid_version = False
    
    if not valid_version:
        utils.log(f'[ERROR] iOS {version} does not exist for device {device_identifier}!\nExiting...', is_verbose)
        sys.exit()

    utils.log(f'[VERBOSE] iOS {version} exists for device {device_identifier}!', is_verbose)

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
        utils.log(f'[ERROR] Device {device_identifier} does not exist!\nExiting...', is_verbose)
        sys.exit()

    utils.log(f'[VERBOSE] Device {device_identifier} exists!', is_verbose)

def fetch_1033_ota_bm(device_identifier, version):
    if version.startswith('10.'):
        manifest_version = '10.3.3'

    if not os.path.isdir('work/'):
        os.makedirs('work/')

    shutil.copy(f'resources/ota_manifests/{manifest_version}/BuildManifest_{device_identifier}.plist', 'work/OTA_BuildManifest.plist')

def fetch_1033_sepbb(device_identifier, version, is_verbose):
    cellular = is_cellular(device_identifier)
    ipswme_device_info = requests.get(f'https://api.ipsw.me/v4/device/{device_identifier}?type=ipsw')
    device_info = ipswme_device_info.json()
    for x in range(0, len(device_info['firmwares'])):
        if device_info['firmwares'][x]['version'] == '10.3.3':
            ipsw_download = device_info['firmwares'][x]['url']
            utils.log(f'[VERBOSE] Found 10.3.3 IPSW to extract SEP from\n[VERBOSE] URL: {ipsw_download}', is_verbose)
            break

    with RemoteZip(ipsw_download) as ipsw:
        os.makedirs('work/tmp/1033_SEPBB')
        ipsw.extract(f'Firmware/all_flash/sep-firmware.{device_info["boardconfig"][:3]}.RELEASE.im4p', 'work/tmp/1033_SEPBB')
        if cellular:
            ipsw.extract('Firmware/Mav7Mav8-7.60.00.Release.bbfw', 'work/tmp/1033_SEPBB')

    os.rename(f'work/tmp/1033_SEPBB/Firmware/all_flash/sep-firmware.{device_info["boardconfig"][:3]}.RELEASE.im4p', 'work/tmp/1033_SEPBB/sep-firmware.im4p')
    if cellular:
        os.rename(f'work/tmp/1033_SEPBB/Firmware/Mav7Mav8-7.60.00.Release.bbfw', 'work/tmp/1033_SEPBB/baseband.bbfw')

def fetch_ipsw_bm(ipsw_dir, is_verbose):
    os.makedirs('work/tmp/IPSW_BuildManifest')
    with zipfile.ZipFile(ipsw_dir, 'r') as ipsw:
        ipsw.extract('BuildManifest.plist', 'work/tmp/IPSW_BuildManifest')

def check_buildid(firm_bundle):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    if len(data['files']['ramdisk']) == 1:
        return None
    
    buildids = []
    for x in range(0, len(data['files']['ramdisk'])):
        if data['files']['ramdisk'][x]['buildid']:
            buildids.append(data['files']['ramdisk'][x]['buildid'])

    x = input(f'Version with multiple buildids detected, please choose the number of the correct buildid for your IPSW:\n  [1] {buildids[0]}\n  [2] {buildids[1]}\nChoice: ')

    try:
        int(x)
    except ValueError:
        utils.log('[Error] Input not a number!\nExiting...', True)
        sys.exit()

    x = x - 1
    return buildids[x]
