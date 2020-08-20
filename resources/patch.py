import subprocess
import json

def find_firmware_bundle(device_identifier, ios_version, verbose=None):
    pass

def patch_ibss(ibss, verbose=None):
    homebrew_check_process = subprocess.Popen('/usr/bin/which brew', stdout=subprocess.PIPE, shell=True)
    output = str(homebrew_check_process.stdout.read())