import subprocess
import os
import shutil
import json

tempdir_process = subprocess.Popen('/usr/bin/mktemp -d', stdout=subprocess.PIPE, shell=True)
output = str(tempdir_process.stdout.read())
tmpdir = output[2:-3]

def extract_ipsw(ipsw, verbose=None):
    print('This may take a while, please wait!')
    shutil.unpack_archive(ipsw, f'{tmpdir}/ipsw', 'zip')
    ipsw_path = f'{tmpdir}/ipsw'
    if verbose:
        print(f"IPSW extracted at '{ipsw_path}'!")
    return ipsw_path
    
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
        shutil.copyfile(f'{ipsw_path}/{data['files']['ramdisk']['file']}', f'work/unpatched_files/{data['files']['ramdisk']['file']}')
        if verbose:
            print(f'Ramdisk successfully copied to: work/unpatched_files/{data['files']['ramdisk']['file']}')

def extract_asr(ramdisk, verbose=None):
    ramdisk_mount = f'{tmpdir}/dmg'
    if os.path.exists(f''):
        os.makedirs(ramdisk_mount)
    
    subprocess.Popen(f'/usr/bin/hdiutil attach {ramdisk} -mountpoint {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
    if verbose:
        print('Attaching ramdisk with hdiutil...')
    try:
        if verbose:
            print('Copying asr binary from ramdisk to work directory...')
        shutil.copyfile(f'{ramdisk_mount}/usr/sbin/asr', 'work/unpatched_files/asr')
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
        shutil.copyfile(ibss_path, f'work/unpatched_files/iBSS.{hardware_model[:-2]}.RELEASE.im4p')
        if verbose:
            print(f'iBSS copied to work directory')
    if os.path.isfile(f'{ipsw_dir}/Firmware/DFU/iBEC.{hardware_model[:-2]}.RELEASE.im4p'):
        ibec_path = f'{ipsw_dir}/Firmware/DFU/iBEC.{hardware_model[:-2]}.RELEASE.im4p'
        if verbose:
            print(f'iBEC found at: {ibec_path}')
        shutil.copyfile(ibec_path, f'work/unpatched_files/iBEC.{hardware_model[:-2]}.RELEASE.im4p')
        if verbose:
            print(f'iBEC copied to work directory')
    if os.path.isfile(f'{ipsw_dir}/kernelcache.release.{device_identifier[:-2].lower()}'):
        kern_path = f'{ipsw_dir}/kernelcache.release.{device_identifier[:-2].lower()}'
        if verbose:
            print(f'Kernelcache found at: {kern_path}')
        shutil.copyfile(kern_path, f'work/unpatched_files/kernelcache.release.{device_identifier[:-2].lower()}')
        if verbose:
            print(f'Kernelcache copied to work directory')
    return f'iBSS.{hardware_model[:-2]}.RELEASE.im4p', f'iBEC.{hardware_model[:-2]}.RELEASE.im4p', f'kernelcache.release.{device_identifier[:-2].lower()}'