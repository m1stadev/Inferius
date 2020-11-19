import os
import remotezip
import shutil

class IPSW(object):
    def __init__(self, device_identifier, version, ipsw_url):
        super().__init__()

        self.device = device_identifier
        self.ipsw = ipsw_url
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