import json
import os
import subprocess

import bsdiff4


# Applies patches from firmware bundle onto bootchain
def patch_bootchain(firm_bundle, ipsw_path, firm_bundle_number, verbose=None):
    os.makedirs('work/patched_files')
    with open('{}/Info.json'.format(firm_bundle)) as f:
        data = json.load(f)
        if firm_bundle_number != 1337:
            ibss = [data['devices'][firm_bundle_number]['files']['ibss']['file'],
                    data['devices'][firm_bundle_number]['files']['ibss']['patch']]

            ibec = [data['devices'][firm_bundle_number]['files']['ibec']['file'],
                    data['devices'][firm_bundle_number]['files']['ibec']['patch']]

            kernelcache = [data['files']['kernelcache']
                           ['file'], data['files']['kernelcache']['patch']]

            ramdisk = [data['files']['ramdisk']['file'],
                       data['files']['ramdisk']['patch']]
        else:
            ibss = [data['files']['ibss']['file'],
                    data['files']['ibss']['patch']]

            ibec = [data['files']['ibec']['file'],
                    data['files']['ibec']['patch']]

            kernelcache = [data['files']['kernelcache']
                           ['file'], data['files']['kernelcache']['patch']]

            ramdisk = [data['files']['ramdisk']['file'],
                       data['files']['ramdisk']['patch']]

    bsdiff4.file_patch_inplace(
        'work/ipsw/{}'.format(ibss[0]), '{}/{}'.format(firm_bundle, ibss[1]))

    bsdiff4.file_patch_inplace(
        'work/ipsw/{}'.format(ibec[0]), '{}/{}'.format(firm_bundle, ibec[1]))

    bsdiff4.file_patch_inplace(
        'work/ipsw/{}'.format(kernelcache[0]), '{}/{}'.format(firm_bundle, kernelcache[1]))

    bsdiff4.file_patch_inplace(
        'work/ipsw/{}'.format(ramdisk[0]), '{}/{}'.format(firm_bundle, ramdisk[1]))


def sign_ibss_ibec(ibss_path, ibec_path):
    ibss_sign = subprocess.run(
        ('resources/bin/img4tool',
         '-c',
         'work/ipsw/ibss.img4',
         '-p',
         'work/ipsw/{}'.format(ibss_path),
         '-s',
         'work/ipsw/blob.shsh2'),
        stdout=subprocess.PIPE,
        universal_newlines=True)

    if ibss_sign.returncode == 1:
        print('Failed to sign iBSS!')
        raise

    ibec_sign = subprocess.run(
        ('resources/bin/img4tool',
         '-c',
         'work/ipsw/ibec.img4',
         '-p',
         'work/ipsw/{}'.format(ibec_path),
         '-s',
         'work/ipsw/blob.shsh2'),
        stdout=subprocess.PIPE,
        universal_newlines=True)

    if ibec_sign.returncode == 1:
        print('Failed to sign iBEC!')
        raise
