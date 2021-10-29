import shutil
import subprocess
import sys


class Checks:
    def __init__(self):
        self.check_bin('./bin/futurerestore')
        self.check_bin('./bin/tsschecker')
        self.check_bin('./bin/irecovery')
        self.check_bin('./bin/img4tool')

    def check_bin(self, binary):
        if shutil.which(binary) is None:
            sys.exit(f"[ERROR] '{binary}' not found. Exiting.")

        binary_name = binary.split('/')[-1]

        # if binary_name == 'futurerestore':
        #     fr_ver = subprocess.run((binary), stdout=subprocess.PIPE, universal_newlines=True).stdout
        #     if '-m1sta' not in fr_ver.splitlines()[1]:
        #         sys.exit(f"[ERROR] This futurerestore cannot be used with Inferius. Exiting.")

        if binary_name == 'irecovery':
            irec_ver = subprocess.run((binary, '-V'), stdout=subprocess.PIPE, universal_newlines=True).stdout

            if 'unrecognized option' in irec_ver:
                sys.exit(f"[ERROR] Your futurerestore version is too old. Exiting.")
