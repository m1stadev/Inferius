import json
import os
import bsdiff4

def patch_bootchain(firm_bundle, ipsw_path, verbose=None): # Applies patches from firmware bundle onto bootchain
    os.makedirs('work/patched_files', exist_ok = True)
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ibss = [data['files']['ibss']['file'], data['files']['ibss']['patch']]
        ibec = [data['files']['ibec']['file'], data['files']['ibec']['patch']]
        kernelcache = [data['files']['kernelcache']['file'], data['files']['kernelcache']['patch']]
        ramdisk = [data['files']['ramdisk']['file'], data['files']['ramdisk']['patch']]
    bsdiff4.file_patch_inplace(f'work/ipsw/{ibss[0]}', f'{firm_bundle}/{ibss[1]}')
    if verbose:
        print(f'[VERBOSE] iBSS patched and put in work/ipsw/{ibss[0]}')
    bsdiff4.file_patch_inplace(f'work/ipsw/{ibec[0]}', f'{firm_bundle}/{ibec[1]}')
    if verbose:
        print(f'[VERBOSE] iBEC patched and put in work/ipsw/{ibec[0]}')
    bsdiff4.file_patch_inplace(f'work/ipsw/{kernelcache[0]}', f'{firm_bundle}/{kernelcache[1]}')
    if verbose:
        print(f'[VERBOSE] Kernelcache patched and put in work/ipsw/{kernelcache[0]}')
    bsdiff4.file_patch_inplace(f'work/ipsw/{ramdisk[0]}', f'{firm_bundle}/{ramdisk[1]}')
    if verbose:
        print(f'[VERBOSE] Ramdisk patched and put in work/ipsw/{ramdisk[0]}')