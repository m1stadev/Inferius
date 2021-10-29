import glob
import shutil
import subprocess
import os
import sys
import time


class Restore:
    def __init__(self, identifier, platform):
        self.device = identifier
        self.platform = platform

    def restore(self, ipsw, cellular, update):
        args = [
            './bin/futurerestore',
            '-t', self.signing_blob,
            '--latest-sep'
        ]

        if update:
            args.append('-u')

        if cellular:
            args.append('--latest-baseband')
        else:
            args.append('--no-baseband')

        args.append(ipsw)
        with open('futurerestore_error.log', 'w') as f:
            f.write(f"{' '.join(args)}\n\n")

        with open('futurerestore_error.log', 'a') as f:
            futurerestore = subprocess.run(args, stderr=subprocess.DEVNULL, stdout=f, universal_newlines=True)

        if os.path.isdir(ipsw.rsplit('.', 1)[0]):
            shutil.rmtree(ipsw.rsplit('.', 1)[0])

        if 'Done: restoring succeeded!' not in futurerestore.stdout:
            sys.exit("[ERROR] Restore failed. Log written to 'futurerestore_error.log'. Exiting.")
            
        os.remove('futurerestore_error.log')

    def save_blobs(self, ecid, boardconfig, path, apnonce=None):
        args = [
            './bin/tsschecker',
            '-d', self.device,
            '-B', boardconfig,
            '-e', f'0x{ecid}',
            '-l',
            '-s',
            '--save-path', path,
            '--nocache'
        ]

        if apnonce:
            args.append('--apnonce')
            args.append(apnonce)

        tsschecker = subprocess.check_output(args, universal_newlines=True)
        if 'Saved shsh blobs!' not in tsschecker:
            sys.exit('[ERROR] Failed to save blobs. Exiting.')

        if apnonce:
            for blob in glob.glob(f'{path}/*.shsh*'):
                if blob != self.signing_blob:
                    self.blob = blob
                    break
        else:
            self.signing_blob = glob.glob(f'{path}/*.shsh*')[0]

    def send_component(self, file, component):
        if component == 'iBSS' and self.platform in (8960, 8015): #TODO: Reset device via pyusb rather than call an external binary.
            irecovery_reset = subprocess.run(('irecovery', '-f', file), stdout=subprocess.DEVNULL)
            if irecovery_reset.returncode != 0:
                sys.exit('[ERROR] Failed to reset device. Exiting.')

        irecovery = subprocess.run(('./bin/irecovery', '-f', file), stdout=subprocess.DEVNULL)
        if irecovery.returncode != 0:
            sys.exit(f"[ERROR] Failed to send '{component}'. Exiting.")

        if component == 'iBEC':
            if 8010 <= self.platform <= 8015:
                irecovery_jump = subprocess.run(('irecovery', '-c', 'go'), stdout=subprocess.DEVNULL)
                if irecovery_jump.returncode != 0:
                    sys.exit(f"[ERROR] Failed to boot '{component}'. Exiting.")

            time.sleep(3)

    def sign_component(self, file, output):
        args = (
            './bin/img4tool',
            '-c', output,
            '-p', file,
            '-s', self.signing_blob
        )
            
        img4tool = subprocess.run(args, stdout=subprocess.DEVNULL)
        if img4tool.returncode != 0:
            sys.exit(f"[ERROR] Failed to sign '{file.split('/')[-1]}'. Exiting.")
