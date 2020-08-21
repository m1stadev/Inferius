import subprocess
import json
import os
import sys
import bsdiff4
import time
import shutil

def unpack_bootchain(bootchain, firm_bundle, verbose=None): # Extracts (and decrypts if necessary) iBSS, iBEC, and kernelcache.
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ibss_key = data['files']['ibss']['kbag']['key']
        ibss_iv = data['files']['ibss']['kbag']['iv']
        ibec_key = data['files']['ibec']['kbag']['key']
        ibec_iv = data['files']['ibec']['kbag']['iv']
    for x in bootchain:
        if 'iBSS' in x:
            bootchain_type = 'ibss'
            subprocess.Popen(f'./resources/bin/img4tool -e --iv {ibss_iv} --key {ibss_key} -o work/unpatched_files/{bootchain_type}.raw {x}', stdout=subprocess.PIPE, shell=True)
            time.sleep(5)
            if verbose:
                print(f'[VERBOSE] {x} decrypted and extracted to work/unpatched_files/{bootchain_type}.raw')
        elif 'iBEC' in x:
            bootchain_type = 'ibec'
            subprocess.Popen(f'./resources/bin/img4tool -e --iv {ibec_iv} --key {ibec_key} -o work/unpatched_files/{bootchain_type}.raw {x}', stdout=subprocess.PIPE, shell=True)
            time.sleep(5)
            if verbose:
                print(f'[VERBOSE] {x} decrypted and extracted to work/unpatched_files/{bootchain_type}.raw')
        elif 'kernelcache' in x:
            bootchain_type = 'kernelcache'
            subprocess.Popen(f'./resources/bin/img4tool -e -o work/unpatched_files/{bootchain_type}.raw {x}', stdout=subprocess.PIPE, shell=True)
            time.sleep(5)
            if verbose:
                print(f'[VERBOSE] {x} extracted to work/unpatched_files/{bootchain_type}.raw')
    raw_bootchain_path = ['work/unpatched_files/ibss.raw', 'work/unpatched_files/ibec.raw', 'work/unpatched_files/kernelcache.raw']
    return raw_bootchain_path[0], raw_bootchain_path[1], raw_bootchain_path[2]

def patch_bootchain(raw_bootchain, firm_bundle, verbose=None): # Applies patches from firmware bundle onto bootchain
    os.makedirs('work/patched_files', exist_ok = True)
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ibss_patch = data['files']['ibss']['patch']
        ibec_patch = data['files']['ibss']['patch']
        kernelcache_patch = data['files']['kernelcache']['patch']
        asr_patch = data['files']['ramdisk']['patch']
    bsdiff4.file_patch(raw_bootchain[0], 'work/patched_files/ibss.pwn', f'{firm_bundle}/{ibss_patch}')
    if verbose:
        print('[VERBOSE] iBSS patched and put in work/patched_files/ibss.pwn')
    bsdiff4.file_patch(raw_bootchain[1], 'work/patched_files/ibec.pwn', f'{firm_bundle}/{ibec_patch}')
    if verbose:
        print('[VERBOSE] iBEC patched and put in work/patched_files/ibec.pwn')
    bsdiff4.file_patch(raw_bootchain[2], 'work/patched_files/kernelcache.pwn', f'{firm_bundle}/{kernelcache_patch}')
    if verbose:
        print('[VERBOSE] Kernelcache patched and put in work/patched_files/kernelcache.pwn')
    bsdiff4.file_patch(raw_bootchain[3], 'work/patched_files/asr.pwn', f'{firm_bundle}/{asr_patch}')
    if verbose:
        print('[VERBOSE] asr patched and put in work/patched_files/asr.pwn')
    os.chmod('work/patched_files/asr.pwn', int('0775'))
    patched_bootchain = ['work/patched_files/ibss.pwn', 'work/patched_files/ibec.pwn', 'work/patched_files/kernelcache.pwn', 'work/patched_files/asr.pwn']
    return patched_bootchain[0], patched_bootchain[1], patched_bootchain[2], patched_bootchain[3]

def repack_bootchain(bootchain, firm_bundle, ipsw_path, verbose=None): # Repacks patched bootchain.
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ibss = data['files']['ibss']['file']
        ibec = data['files']['ibec']['file']
        kernelcache = data['files']['kernelcache']['file']
        ramdisk = data['files']['ramdisk']['file']
        processor = data['processor']
        processor = processor.lower()
    subprocess.Popen(f'./resources/bin/img4tool -c {ipsw_path}/{ibss} -t ibss {bootchain[0]}', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    if verbose:
        print('[VERBOSE] Repacked patched iBSS into IM4P')
    subprocess.Popen(f'./resources/bin/img4tool -c {ipsw_path}/{ibec} -t ibec {bootchain[1]}', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    if verbose:
        print('[VERBOSE] Repacked patched iBEC into IM4P')
    if processor.startswith('t') and int(processor[1:]) >= 8010:
        compression = 'bvx2'
    else:
        compression = 'complzss'
    subprocess.Popen(f'./resources/bin/img4tool -c {ipsw_path}/{kernelcache} -t krnl {bootchain[2]} --compression {compression}', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    if verbose:
        print(f'[VERBOSE] Repacked patched Kernelcache into IM4P with {compression} compression')
    subprocess.Popen(f'./resources/bin/img4tool -c {ipsw_path}/{ramdisk} -t rdsk {bootchain[3]}', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    if verbose:
        print('[VERBOSE] Repacked patched ramdisk into IM4P')

def repack_asr(asr_path, ramdisk, verbose=None):
    ramdisk_mount = 'work/patched_files/dmg'
    if verbose:
        print('[VERBOSE] Mounting ramdisk...')
    subprocess.Popen(f'./resources/bin/img4tool -e -o work/patched_files/ramdisk.dmg {ramdisk}', stdout=subprocess.PIPE, shell=True)
    time.sleep(10)
    subprocess.Popen(f'/usr/bin/hdiutil attach work/patched_files/ramdisk.dmg -mountpoint {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
    time.sleep(5)
    if verbose:
        print('[VERBOSE] Copying patched asr binary into ramdisk...')
    shutil.copy(asr_path, f'{ramdisk_mount}/usr/sbin/asr')
    return 'work/patched_files/ramdisk.dmg'