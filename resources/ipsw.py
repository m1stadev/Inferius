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
            print(f'[VERBOSE] {ipsw} is a zip archive!')
    else:
        sys.exit(f'{ipsw} is not a valid IPSW!\nExiting...')
    if ipsw.endswith('.ipsw'):
        print('Extracting IPSW. This may take a while, please wait...')
        with zipfile.ZipFile(ipsw, 'r') as zip_ref:
            zip_ref.extractall(f'{tmpdir}/ipsw')
    if verbose:
        print(f'[VERBOSE] IPSW extracted to: {tmpdir}/ipsw')
    return f'{tmpdir}/ipsw'
    
def find_bundle(device_identifier, version, verbose=None):
    if os.path.isdir(f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'):
        if verbose:
            print(f'[VERBOSE] Firmware bundle exists at: resources/FirmwareBundles/{device_identifier}_{version}_bundle')
        return f'resources/FirmwareBundles/{device_identifier}_{version}_bundle'
    else:
        sys.exit(f"Firmware bundle for\nDevice: {device_identifier}\nVersion: {version}\ndoesn't exist!\nIf you have provided your own firmware bundle,\nplease make sure it is in 'resources/FirmwareBundles'\nand named {device_identifier}_{version}_bundle")

def grab_ramdisk(ipsw_path, firm_bundle, verbose=None):
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ramdisk_file = data['files']['ramdisk']['file']
        f.close()
    os.makedirs('work/unpatched_files/', exist_ok = True)
    shutil.copy(f'{ipsw_path}/{ramdisk_file}', f'work/unpatched_files/{ramdisk_file}')
    if verbose:
        print(f'[VERBOSE] Ramdisk successfully copied to: work/unpatched_files/{ramdisk_file}')
    ramdisk_path = f'work/unpatched_files/{ramdisk_file}'
    return ramdisk_path

def extract_asr(ramdisk, verbose=None):
    ramdisk_mount = 'work/unpatched_files/dmg'
    if verbose:
        print('[VERBOSE] Extracting ramdisk dmg...')
    subprocess.Popen(f'./resources/bin/img4tool -e -o work/unpatched_files/ramdisk.dmg {ramdisk}', stdout=subprocess.PIPE, shell=True)
    if verbose:
        print('[VERBOSE] Mounting ramdisk...')
    subprocess.Popen(f'/usr/bin/hdiutil attach work/unpatched_files/ramdisk.dmg -mountpoint work/unpatched_files/dmg', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    try:
        if verbose:
            print('[VERBOSE] Copying asr binary from ramdisk to work directory...')
        shutil.copy(f'{ramdisk_mount}/usr/sbin/asr', 'work/unpatched_files/asr')
    except FileNotFoundError:
        if verbose:
            print("[VERBOSE] asr binary not found, dmg must not be mounted! Make sure you don't have any other DMGs mounted, then run the script again\nExiting...")
        subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
        raise
    subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)

def grab_bootchain(ipsw_path, firm_bundle, verbose=None):
    bootchain = []
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        bootchain.append(data['files']['ibss']['file'])
        bootchain.append(data['files']['ibec']['file'])
        bootchain.append(data['files']['kernelcache']['file'])
        f.close()
    for b in bootchain:
        shutil.copy(f'{ipsw_path}/{b}', f'work/unpatched_files')
        if verbose:
            print(f'[VERBOSE] {b} successfully copied to work/unpatched_files')
    print('Bootchain successfully copied to work directory!')
    ibss_path = bootchain[0]
    ibss_path = f'work/unpatched_files/{ibss_path[13:]}'
    ibec_path = bootchain[1]
    ibec_path = f'work/unpatched_files/{ibec_path[13:]}'
    kernelcache_path = f'work/unpatched_files/{bootchain[2]}'
    return ibss_path, ibec_path, kernelcache_path