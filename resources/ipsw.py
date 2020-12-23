import hashlib
import os
import requests
import remotezip
import shutil

class IPSW(object):
    def __init__(self, device_identifier, ipsw):
        super().__init__()

        self.device = device_identifier
        self.ipsw = ipsw

    def verify_ipsw(self, version):
        data = requests.get(f'https://api.ipsw.me/v4/device/{self.device}?type=ipsw').json()

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
            except FileNotFoundError:
                sys.exit(f'[ERROR] IPSW does not exist at path: {self.ipsw}. Exiting...')
            except OSError:
                sys.exit('[ERROR] Ran out of storage while extracting IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...', is_verbose)