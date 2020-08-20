import subprocess
import os
import shutil

tempdir_process = subprocess.Popen('/usr/bin/mktemp -d', stdout=subprocess.PIPE, shell=True)
tmpdir = str(tempdir_process.stdout.read())
tmpdir = tmpdir[2:-3]

def extract_ipsw(ipsw, verbose=None):
    print('This may take a while, please wait!\n')
    shutil.unpack_archive(ipsw, f'{tmpdir}/ipsw', 'zip')
    ipsw_path = f'{tmpdir}/ipsw'
    if verbose:
        print(f"IPSW extracted at '{ipsw_path}'!\n")
    return ipsw_path
    

def find_ramdisk(ipsw_dir, verbose=None):
    dmg_list = []
    dmgs_list = []
    if 'BuildManifest.plist' not in os.listdir(ipsw_dir):
        print('Error, IPSW does not exist at current directory! Exiting.')
        raise Exception('Error, IPSW does not exist at current directory! Exiting.')
    for file in os.listdir(ipsw_dir):
        if file.endswith('.dmg'):
            if file.startswith('._'):
                continue
            dmg_list.append(str(file))
            dmgs_list.append((os.path.getsize(f'/Volumes/My Shit/Apple/IPSWs/iPhone6,1/10.2/10.2/{file}')))

    smallest_dmg = dmgs_list.index(min(dmgs_list))
    if verbose:
        print(f'Ramdisk found: {dmg_list[smallest_dmg]}')
    return dmg_list[smallest_dmg]

def extract_asr(ramdisk, verbose=None):
    ramdisk_mount = f'{tmpdir}/dmg'
    if os.path.exists(f''):
        os.makedirs(ramdisk_mount)
    
    subprocess.Popen(f'/usr/bin/hdiutil attach {ramdisk} -mountpoint {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
    if verbose:
        print('Attaching ramdisk with hdiutil...\n')
    try:
        if verbose:
            print('Copying asr binary from ramdisk to work directory...\n')
        shutil.copyfile(f'{ramdisk_mount}/usr/sbin/asr', 'work/unpatched_files/asr')
    except FileNotFoundError:
        if verbose:
            print("asr binary not found, dmg must not be mounted! Make sure you don't have any other DMGs mounted, then run the script again\nExiting...")
        subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
        raise
    subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)

def find_bootchain(ipsw_dir, hardware_model, device_identifier, verbose=None):
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