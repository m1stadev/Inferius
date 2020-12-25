import glob
import os
import subprocess
import sys

class Restore(object):
    def __init__(self, device_identifier, platform):
        super().__init__()

        self.device = device_identifier
        self.platform = platform

    def save_blobs(self, boardconfig, ecid, apnonce, path):
        tsschecker = subprocess.run(('tsschecker', '-d', self.device, '-l', '-e', f'0x{ecid}', '-s', '--apnonce', apnonce, '--save-path', path), stdout=subprocess.PIPE, universal_newlines=True)

        if tsschecker.returncode != 0:
            sys.exit('[ERROR] Failed to save blobs. Exiting...')

        for f in glob.glob(path):
            if f.endswith('.shsh2'):
                self.blob = f
                break

    def sign_component(self, file, output):
        img4tool = subprocess.run(('img4tool', '-c', f'{output}/{file.split("/")[-1].rsplit(".", 1)[0]}.img4', '-p', file, '-s', self.blob), stdout=subprocess.PIPE, universal_newlines=True)

        if img4tool.returncode != 0:
            sys.exit(f"[ERROR] Failed to sign '{file.split('/')[-1]}'. Exiting...")

    def send_component(self, file, component):
        if component = 'iBSS' and self.platform in (8960, 8015):
            irecovery_reset = subprocess.run(('irecovery', '-r'), stdout=subprocess.PIPE, universal_newlines=True)

            if irecovery_reset.returncode != 0:
                sys.exit(f'[ERROR] Failed to reset connection. Exiting...')

        irecovery = subprocess.run(('irecovery', '-f', file), stdout=subprocess.PIPE, universal_newlines=True)
        if irecovery.returncode != 0:
            sys.exit(f'[ERROR] Failed to send {component}. Exiting...')

        if component = 'iBEC' and 8010 <= self.platform <= 8015:
            irecovery_jump = subprocess.run(('irecovery', '-c', 'go'), stdout=subprocess.PIPE, universal_newlines=True)

            if irecovery_jump.returncode != 0:
                sys.exit(f'[ERROR] Failed to boot {component}. Exiting...')

    def restore(self, ipsw, baseband, update):
        if baseband:
            baseband == '--latest-baseband'
        else:
            baseband = '--no-baseband'

        args = [
            'futurerestore',
            '-t',
            self.blob,
            '--latest-sep',
            baseband,
            ipsw
        ]

        if update:
            args.insert(3, '-u')

        futurerestore = subprocess.run(args)

        if futurerestore.returncode != 0:
            sys.exit('[ERROR] Restore failed. Exiting...')