import shutil
import subprocess
import sys


class Checks:
    def __init__(self):
        self.check_bin('futurerestore')
        self.check_bin('tsschecker')
        self.check_bin('irecovery')
        self.check_bin('img4tool')

    def check_bin(self, binary):
        if shutil.which(binary) is None:
            sys.exit(f"[ERROR] '{binary}' is not installed on your system. Exiting.")

        if binary == 'futurerestore':
            fr_ver = subprocess.run((binary), stdout=subprocess.PIPE, universal_newlines=True).stdout
            if '-m1sta' not in fr_ver.splitlines()[1]:
                sys.exit(f"[ERROR] This futurerestore build cannot be used with Inferius. Exiting.")

        elif binary == 'irecovery':
            try:
                subprocess.check_call((binary, '-V'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                sys.exit(f"[ERROR] Your irecovery version is too old. Exiting.")
