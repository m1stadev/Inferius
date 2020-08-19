import argparse
import os
import shutil
import subprocess

verbose = False

ramdisk = '/Users/m1staawesome/inferius/ramdisk.dmg'

tempdir_process = subprocess.Popen('/usr/bin/mktemp -d', stdout=subprocess.PIPE, shell=True)
tmpdir = tempdir_process.stdout.read()
tmpdir = tmpdir[2:-3]
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
    exit()
hdiutil_process = subprocess.Popen(f'/usr/bin/hdiutil detach {ramdisk_mount}', stdout=subprocess.PIPE, shell=True)
