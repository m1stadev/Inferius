import subprocess
import json

def decrypt_bootchain(bootchain, firm_bundle, verbose=None): # Extracts (and decrypts if necessary) iBSS, iBEC, and kernelcache.
    with open(f'{firm_bundle}/Info.json') as f:
        data = json.load(f)
        ibss_key = data['files']['ibss']['kbag']['key']
        ibss_iv = data['files']['ibss']['kbag']['iv']
        ibec_key = data['files']['ibec']['kbag']['key']
        ibec_iv = data['files']['ibec']['kbag']['iv']
    for x in bootchain:
        if 'iBSS' in x:
            bootchain_type = 'ibss'
        elif 'iBEC' in x:
            bootchain_type = 'ibec'
        elif 'kernelcache' in x:
            bootchain_type = 'kernelcache'
            if bootchain_type == 'ibss':
                subprocess.Popen(f'./resources/bin/img4tool -e --iv {ibss_iv} --key {ibss_key} -o work/unpatched_files/{bootchain_type}.raw {bootchain}', stdout=subprocess.PIPE, shell=True)
            elif bootchain_type == 'ibec':
                subprocess.Popen(f'./resources/bin/img4tool -e --iv {ibec_iv} --key {ibec_key} -o work/unpatched_files/{bootchain_type}.raw {bootchain}', stdout=subprocess.PIPE, shell=True)
            if verbose:
                print(f'[VERBOSE] {bootchain} decrypted and extracted to work/unpatched_files/{bootchain_type}.raw')
        elif 'kernelcache' == bootchain_type:
            subprocess.Popen(f'./resources/bin/img4tool -e -o {bootchain_type}.raw {bootchain}', stdout=subprocess.PIPE, shell=True)
            if verbose:
                print(f'[VERBOSE] {bootchain} extracted to work/unpatched_files/{bootchain_type}.raw')
        raw_bootchain_path = ['work/unpatched_files/ibss.raw', 'work/unpatched_files/ibec.raw', 'work/unpatched_files/kernelcache.raw']
        return raw_bootchain_path[0], raw_bootchain_path[1], raw_bootchain_path[2]

def patch_bootchain(bootchain, firm_bundle, verbose=None):
    pass