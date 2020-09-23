from . import utils
import bsdiff4
import json
import os
import subprocess

def patch_bootchain(firm_bundle, firm_bundle_number, is_verbose): # Applies patches from firmware bundle onto bootchain
    os.makedirs('work/patched_files', exist_ok = True)

    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        if firm_bundle_number != 1337:
            ibss = [data['devices'][firm_bundle_number]['files']['ibss']['file'], data['devices'][firm_bundle_number]['files']['ibss']['patch']]
            ibec = [data['devices'][firm_bundle_number]['files']['ibec']['file'], data['devices'][firm_bundle_number]['files']['ibec']['patch']]
            kernelcache = [data['files']['kernelcache']['file'], data['files']['kernelcache']['patch']]
            ramdisk = [data['files']['ramdisk']['file'], data['files']['ramdisk']['patch']]
        else:
            ibss = [data['files']['ibss']['file'], data['files']['ibss']['patch']]
            ibec = [data['files']['ibec']['file'], data['files']['ibec']['patch']]
            kernelcache = [data['files']['kernelcache']['file'], data['files']['kernelcache']['patch']]
            ramdisk = [data['files']['ramdisk']['file'], data['files']['ramdisk']['patch']]

    bsdiff4.file_patch_inplace(f'work/ipsw/{ibss[0]}', f'{firm_bundle}/{ibss[1]}')
    utils.print_and_log(f'[VERBOSE] iBSS patched and put in work/ipsw/{ibss[0]}', is_verbose)

    bsdiff4.file_patch_inplace(f'work/ipsw/{ibec[0]}', f'{firm_bundle}/{ibec[1]}')
    utils.print_and_log(f'[VERBOSE] iBEC patched and put in work/ipsw/{ibec[0]}', is_verbose)

    bsdiff4.file_patch_inplace(f'work/ipsw/{kernelcache[0]}', f'{firm_bundle}/{kernelcache[1]}')
    utils.print_and_log(f'[VERBOSE] Kernelcache patched and put in work/ipsw/{kernelcache[0]}', is_verbose)

    bsdiff4.file_patch_inplace(f'work/ipsw/{ramdisk[0]}', f'{firm_bundle}/{ramdisk[1]}')
    utils.print_and_log(f'[VERBOSE] Ramdisk patched and put in work/ipsw/{ramdisk[0]}', is_verbose)

def sign_ibss_ibec(ibss_path, ibec_path, is_verbose):
    subprocess.run(f'./resources/bin/img4tool -c work/ipsw/ibss.img4 -p work/ipsw/{ibss_path} -s work/ipsw/blob.shsh2', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.print_and_log('[VERBOSE] iBSS packed into img4', is_verbose)

    subprocess.Popen(f'./resources/bin/img4tool -c work/ipsw/ibec.img4 -p work/ipsw/{ibec_path} -s work/ipsw/blob.shsh2', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    utils.print_and_log('[VERBOSE] iBEC packed into img4', is_verbose)