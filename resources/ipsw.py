import hashlib
import os
import requests
import remotezip
import shutil

class IPSW(object):
    def __init__(self, device_identifier, version, ipsw):
        super().__init__()

        self.device = device_identifier
        self.ipsw = ipsw
        self.version = version
        self.manifest = self.download_manifest()
        self.restoremanifest = self.download_restoremanifest()

    def download_manifest(self):
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10 7 4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        }

        try:
            with remotezip.RemoteZip(self.ipsw, headers=headers) as f:
                f.extract('BuildManifest.plist', '.tmp/mass-decryptor')

        except remotezip.RemoteIOError:
            print(f"[ERROR] Unable to extract bootchain from iOS {self.version}'s IPSW. Continuing...")
            return False

        return '.tmp/mass-decryptor/BuildManifest.plist'

    def download_restoremanifest(self):
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10 7 4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        }

        try:
            with remotezip.RemoteZip(self.ipsw, headers=headers) as f:
                f.extract('Restore.plist', '.tmp/mass-decryptor')

        except remotezip.RemoteIOError:
            print(f"[ERROR] Unable to extract bootchain from iOS {self.version}'s IPSW. Continuing...")
            return False

        return '.tmp/mass-decryptor/Restore.plist'

    def download_components(self, components):
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10 7 4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
        }

        self.components = components

        try:
            with remotezip.RemoteZip(self.ipsw, headers=headers) as f:
                for x in self.components:
                    if self.components[x]['encrypted']:
                        f.extract(self.components[x]['path'], '.tmp/mass-decryptor')

        except remotezip.RemoteIOError:
            print(f"[ERROR] Unable to extract bootchain from iOS {self.version}'s IPSW. Continuing...")
            return False

        for x in self.components:
            if self.components[x]['encrypted']:
                shutil.move(f'.tmp/mass-decryptor/{self.components[x]["path"]}', f'.tmp/mass-decryptor/{self.components[x]["file"]}')

        shutil.rmtree('.tmp/mass-decryptor/Firmware')
        return True

    def verify_ipsw(self):
        data = requests.get(f'https://api.ipsw.me/v4/device/{self.device}?type=ipsw').json()
        data = api_data.json()

        ipsw_sha1 = [data['firmwares'][x]['sha1sum'] for x in range(len(data['firmwares'])) if data['firmwares'][x]['version'] == self.version][0]

        with open(ipsw_dir, 'rb') as f:
            sha1 = hashlib.sha1()
            file_buffer = f.read(8192)
            while len(file_buffer) > 0:
                sha1.update(file_buffer)
                file_buffer = f.read(8192)

        if ipsw_sha1 != sha1.hexdigest():
            sys.exit('[ERROR] IPSW is not valid. Redownload the IPSW then try again. Exiting...')

    def extract_ipsw(self, path):
        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            try:
                ipsw.extractall(path)
            except OSError:
                sys.exit('[ERROR] Ran out of storage while extracting IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...', is_verbose)