import subprocess
import os
import shutil
import json
import sys
import time
import zipfile

tempdir_process = subprocess.Popen('/usr/bin/mktemp -d', stdout=subprocess.PIPE, shell=True)
output = str(tempdir_process.stdout.read())
tmpdir = output[2:-3]

def extract_ipsw(ipsw, verbose=None):
    if not os.path.exists(ipsw):
        sys.exit(f"IPSW at '{ipsw}' doesn't exist!\nExiting...")
    if zipfile.is_zipfile(ipsw):
        pass
        if verbose:
            print(f'{ipsw} is a zip archive!')
    else:
        sys.exit(f'{ipsw} is not a valid IPSW!\nExiting...')
    if ipsw.endswith('.ipsw'):
        print('Extracting IPSW. This may take a while, please wait...')
        with zipfile.ZipFile(ipsw, 'r') as zip_ref:
            zip_ref.extractall(f'{tmpdir}/ipsw')
    if verbose:
        print(f'IPSW extracted to: {tmpdir}/ipsw')
    return f'{tmpdir}/ipsw'
    
def find_bundle(device_identifier, version, verbose=None):
    if os.path.isdir(f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'):
        if verbose:
            print(f'Firmware bundle exists!\nDirectory: resources/FirmwareBundles/{device_identifier}_{version}_bundle')
        return f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'
    else:
        print(f"Firmware bundle for\nDevice: {device_identifier}\nVersion: {version}\ndoesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named {device_identifier}_{version}_bundle")

def grab_ramdisk(ipsw_path, firm_bundle, verbose=None):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ramdisk_file = data['files']['ramdisk']['file']
        f.close()
    os.makedirs('work/unpatched_files/', exist_ok = True)
    shutil.copy(f'{ipsw_path}/{ramdisk_file}', f'work/unpatched_files/{ramdisk_file}')
    if verbose:
        print(f'Ramdisk successfully copied to: work/unpatched_files/{ramdisk_file}')
    ramdisk_path = f'work/unpatched_files/{ramdisk_file}'
    return ramdisk_path

def extract_asr(ramdisk, verbose=None):
    ramdisk_mount = f'{tmpdir}/dmg'
    if verbose:
        print('Extracting ramdisk dmg from im4p')
    subprocess.Popen(f'./resources/bin/img4tool -e -o work/unpatched_files/ramdisk.dmg {ramdisk}', stdout=subprocess.PIPE, shell=True)
    if verbose:
        print('Mounting ramdisk...')
    subprocess.Popen(f'/usr/bin/hdiutil attach work/unpatched_files/ramdisk.dmg -mountpoint {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    try:
        if verbose:
            print('Copying asr binary from ramdisk to work directory...')
        shutil.copy(f'{ramdisk_mount}/usr/sbin/asr', 'work/unpatched_files/asr')
    except FileNotFoundError:
        if verbose:
            print("asr binary not found, dmg must not be mounted! Make sure you don't have any other DMGs mounted, then run the script again\nExiting...")
        subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
        raise
    subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)

def grab_bootchain(ipsw_dir, hardware_model, device_identifier, verbose=None):
    if os.path.isfile(f'{ipsw_dir}/Firmware/DFU/iBSS.{hardware_model[:-2]}.RELEASE.im4p'):
        ibss_path = f'{ipsw_dir}/Firmware/DFU/iBSS.{hardware_model[:-2]}.RELEASE.im4p'
        if verbose:
            print(f'iBSS found at: {ibss_path}')
        shutil.copy(ibss_path, f'work/unpatched_files/iBSS.{hardware_model[:-2]}.RELEASE.im4p')
        if verbose:
            print(f'iBSS copied to work directory')
    if os.path.isfile(f'{ipsw_dir}/Firmware/DFU/iBEC.{hardware_model[:-2]}.RELEASE.im4p'):
        ibec_path = f'{ipsw_dir}/Firmware/DFU/iBEC.{hardware_model[:-2]}.RELEASE.im4p'
        if verbose:
            print(f'iBEC found at: {ibec_path}')
        shutil.copy(ibec_path, f'work/unpatched_files/iBEC.{hardware_model[:-2]}.RELEASE.im4p')
        if verbose:
            print(f'iBEC copied to work directory')
    if os.path.isfile(f'{ipsw_dir}/kernelcache.release.{device_identifier[:-2].lower()}'):
        kern_path = f'{ipsw_dir}/kernelcache.release.{device_identifier[:-2].lower()}'
        if verbose:
            print(f'Kernelcache found at: {kern_path}')
        shutil.copy(kern_path, f'work/unpatched_files/kernelcache.release.{device_identifier[:-2].lower()}')
        if verbose:
            print(f'Kernelcache copied to work directory')
    return f'iBSS.{hardware_model[:-2]}.RELEASE.im4p', f'iBEC.{hardware_model[:-2]}.RELEASE.im4p', f'kernelcache.release.{device_identifier[:-2].lower()}'