from . import utils
import bsdiff4
import json
import os

def patch_bootchain(firm_bundle, firm_bundle_number, buildid, is_verbose): # Applies patches from firmware bundle onto bootchain
    os.makedirs('work/patched_files', exist_ok = True)
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)

    if buildid:
        for x in range(0, len(data['files'])):
            if data['files'][x]['buildid'] == buildid:
                ramdisk_path = data['files']['ramdisk'][x]['file']
                ramdisk_patch = data['files']['ramdisk'][x]['patch']
                kernelcache_path = data['files']['kernelcache'][x]['file']
                kernelcache_patch = data['files']['kernelcache'][x]['patch']
                break
    else:
        ramdisk_path = data['files']['ramdisk']['file']
        ramdisk_patch = data['files']['ramdisk']['patch']
        kernelcache_path = data['files']['kernelcache']['file']
        kernelcache_patch = data['files']['kernelcache']['patch']

    if firm_bundle_number != 1337:
        ibss = [data['devices'][firm_bundle_number]['files']['ibss']['file'], data['devices'][firm_bundle_number]['files']['ibss']['patch']]
        ibec = [data['devices'][firm_bundle_number]['files']['ibec']['file'], data['devices'][firm_bundle_number]['files']['ibec']['patch']]
        kernelcache = [kernelcache_path, kernelcache_patch]
        ramdisk = [ramdisk_path, ramdisk_patch]
    else:
        ibss = [data['files']['ibss']['file'], data['files']['ibss']['patch']]
        ibec = [data['files']['ibec']['file'], data['files']['ibec']['patch']]
        kernelcache = [kernelcache_path, kernelcache_patch]
        ramdisk = [ramdisk_path, ramdisk_patch]

    bsdiff4.file_patch_inplace(f'work/ipsw/{ibss[0]}', f'{firm_bundle}/{ibss[1]}')
    utils.log(f'[VERBOSE] iBSS patched and put in work/ipsw/{ibss[0]}', is_verbose)

    bsdiff4.file_patch_inplace(f'work/ipsw/{ibec[0]}', f'{firm_bundle}/{ibec[1]}')
    utils.log(f'[VERBOSE] iBEC patched and put in work/ipsw/{ibec[0]}', is_verbose)

    bsdiff4.file_patch_inplace(f'work/ipsw/{kernelcache[0]}', f'{firm_bundle}/{kernelcache[1]}')
    utils.log(f'[VERBOSE] Kernelcache patched and put in work/ipsw/{kernelcache[0]}', is_verbose)

    bsdiff4.file_patch_inplace(f'work/ipsw/{ramdisk[0]}', f'{firm_bundle}/{ramdisk[1]}')
    utils.log(f'[VERBOSE] Ramdisk patched and put in work/ipsw/{ramdisk[0]}', is_verbose)