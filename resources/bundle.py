import bsdiff4
import requests
import os
import sys
import usb
import zipfile

class Bundle(object):
    def __init__(self, ipsw_path):
        super().__init__()

        self.ipsw = ipsw_path

    def fetch_bundle(self, device, version):
        bundle = requests.get(f'https://github.com/marijuanARM/inferius-bundles/raw/master/{device}_{version}_bundle.zip')
        if bundle.status_code == 404:
            sys.exit(f'[ERROR] A Firmware Bundle does not exist for device: {device}, version: {version}. Exiting...')

        os.makedirs(f'.tmp/Inferius/{self.device}_{self.version}_bundle')

        with open(f'.tmp/Inferius/{self.device}_{self.version}_bundle.zip', 'wb') as f:
            f.write(bundle.content)

        with zipfile.ZipFile(f'.tmp/Inferius/{self.device}_{self.version}_bundle.zip', 'r') as f:
            try:
                f.extractall(f'.tmp/Inferius/{self.device}_{self.version}_bundle')
            except OSError:
                sys.exit('[ERROR] Ran out of storage while extracting Firmware Bundle. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...', is_verbose)

        self.bundle = f'.tmp/Inferius/{self.device}_{self.version}_bundle'

    def apply_patches(self):
        with open(f'{self.bundle}/Info.json', 'r') as f:
            bundle_data = f.read()

        #TODO: actually do this lol