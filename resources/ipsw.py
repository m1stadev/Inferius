import hashlib
import os
import shutil
import sys
import time
import zipfile

class IPSW(object):
    def __init__(self, device_identifier, ipsw):
        super().__init__()

        self.device = device_identifier
        self.ipsw = ipsw

    def verify_ipsw(self, ipsw_sha1):
        with open(self.ipsw, 'rb') as f:
            sha1 = hashlib.sha1()
            file_buffer = f.read(8192)
            while len(file_buffer) > 0:
                sha1.update(file_buffer)
                file_buffer = f.read(8192)

        if ipsw_sha1 != sha1.hexdigest():
            sys.exit(f'[ERROR] IPSW at path: {self.ipsw} is not valid. Redownload the IPSW then try again. Exiting...')

    def extract_ipsw(self, path):
        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            try:
                ipsw.extractall(path)
            except FileNotFoundError:
                sys.exit(f'[ERROR] IPSW does not exist at path: {self.ipsw}. Exiting...')
            except zipfile.BadZipFile:
                sys.exit(f'[ERROR] IPSW at path: {self.ipsw} is not a valid zip archive. Redownload the IPSW then try again. Exiting...')
            except OSError:
                sys.exit('[ERROR] Ran out of storage while extracting IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...')

    def extract_file(self, file, path):
        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            try:
                ipsw.extract(file, path)
            except FileNotFoundError:
                sys.exit(f'[ERROR] IPSW does not exist at path: {self.ipsw}. Exiting...')
            except zipfile.BadZipFile:
                sys.exit(f'[ERROR] IPSW at path: {self.ipsw} is not a valid zip archive. Redownload the IPSW then try again. Exiting...')
            except KeyError:
                sys.exit(f'[ERROR] IPSW at path: {self.ipsw} is not valid. Redownload the IPSW then try again. Exiting...')
            except OSError:
                sys.exit(f"[ERROR] Ran out of storage while extracting '{file}' from IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...")

    def create_ipsw(self, path, output, update_support):
        if not os.path.isdir('IPSWs'):
            os.mkdir('IPSWs')

        if not update_support:
            with open(f'{path}/.no_update_support', 'w') as f:
                pass

        with open(f'{path}/.Inferius', 'w') as f:
            pass

        try:
            shutil.make_archive(f'IPSWs/{output}', 'zip', path)
        except OSError:
            sys.exit(f'[ERROR] Ran out of storage while creating IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...')

        os.rename(f'IPSWs/{output}.zip', f'IPSWs/{output}')

        return f'IPSWs/{output}'

    def verify_custom_ipsw(self, update_support):
        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            try:
                if '.Inferius' not in ipsw.namelist():
                    sys.exit('[ERROR] This IPSW was not created by Inferius. Exiting...')
                
                if '.no_update_support' in ipsw.namelist() and update_support == True:
                    sys.exit('[ERROR] This IPSW does not have support for restoring while keeping data. Exiting...')
            except FileNotFoundError:
                sys.exit(f'[ERROR] IPSW does not exist at path: {self.ipsw}. Exiting...')
            except zipfile.BadZipFile:
                sys.exit(f'[ERROR] IPSW at path: {self.ipsw} is not a valid zip archive. Redownload the IPSW then try again. Exiting...')
