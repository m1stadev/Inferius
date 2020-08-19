import subprocess
import os
import shutil
import plistlib

tempdir_process = subprocess.Popen('/usr/bin/mktemp -d', stdout=subprocess.PIPE, shell=True)
tmpdir = str(tempdir_process.stdout.read())
tmpdir = tmpdir[2:-3]

def extract_asr(ramdisk, verbose=None):
    if verbose:
        print(f'created temp dir at: {tmpdir}')
    ramdisk_mount = f'{tmpdir}/dmg'
    if os.path.exists(f''):
        os.makedirs(ramdisk_mount)
    hdiutil_process = subprocess.Popen(f'/usr/bin/hdiutil attach {ramdisk} -mountpoint {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
    if verbose:
        print(hdiutil_process.stdout.read())
    try:
        shutil.copyfile(f'{ramdisk_mount}/usr/sbin/asr', 'work/unpatched_files/asr')
    except FileNotFoundError:
        print("asr binary not found, dmg must not be mounted! make sure you don't have any other DMGs mounted, then run the script again\nExiting...")
        raise
    hdiutil_process = subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)

def extract_ipsw(ipsw, verbose=None):
#    print('This may take a while and freeze your PC, please wait!')
#    shutil.unpack_archive(ipsw, f'{tmpdir}/ipsw', 'zip')
#    print(f"IPSW extracted at '{tmpdir}/ipsw'!")
    ipsw_path = f'{tmpdir}/ipsw'
#    for file in os.listdir(f'{tmpdir}/ipsw'):
#        if 'iBSS' in file:
#            ibss = file
#        if 'iBEC' in file:
#            ibec = file
    
    pl = plistlib.readPlist('BuildManifest.plist')
    for x in pl.items():
        print(x)
        exit()
    print(pl['BuildIdentities'])

def find_ramdisk(verbose=None):
    dmg_list = []
    dmgs_list = []
    for file in os.listdir('/Volumes/My Shit/Apple/IPSWs/iPhone6,1/10.2/10.2/'):
        if file.endswith('.dmg'):
            if file.startswith('._'):
                continue
            dmg_list.append(str(file))
            dmgs_list.append((os.path.getsize(f'/Volumes/My Shit/Apple/IPSWs/iPhone6,1/10.2/10.2/{file}')))

    smallest_dmg = dmgs_list.index(min(dmgs_list))

    return dmg_list[smallest_dmg]
    print(f'Ramdisk = {dmg_list[smallest_dmg]}')



