import glob
import hashlib
import os
import sys
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
                sys.exit(f"[ERROR] Ran out of storage while extracting '{file}'' from IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...")

    def create_ipsw(self, path, output):
        if not os.path.isdir('IPSWs'):
            os.mkdir('IPSWs')

        try:
            with zipfile.ZipFile(f'IPSWs/{output}', 'w') as ipsw:
                for x in glob.glob(f'{path}/*/*/*'):
                    ipsw.write(x, x[len(path) + 1:])

        except OSError as e:
            sys.exit(f'[ERROR] Ran out of storage while creating IPSW. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting...\nerror: {e}')