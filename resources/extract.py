import subprocess
import os
import shutil

tempdir_process = subprocess.Popen('/usr/bin/mktemp -d', stdout=subprocess.PIPE, shell=True)
tmpdir = str(tempdir_process.stdout.read())
tmpdir = tmpdir[2:-3]

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
        print("asr binary not found, dmg must not be mounted! Make sure you don't have any other DMGs mounted, then run the script again\nExiting...")
        subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
        raise
        exit()
    subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)

def extract_ipsw(ipsw, verbose=None):
    print('This may take a while and freeze your PC, please wait!\n')
    shutil.unpack_archive(ipsw, f'{tmpdir}/ipsw', 'zip')
    ipsw_path = f'{tmpdir}/ipsw'
    print(f"IPSW extracted at '{ipsw_path}'!\n")
    if verbose:
        print('Finding ramdisk...\n')
        restore_ramdisk = find_ramdisk(ipsw_path, 'yes')
        print('Ramdisk found! Starting asr extraction process...')
    else:
        restore_ramdisk = find_ramdisk(ipsw_path)
    

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



