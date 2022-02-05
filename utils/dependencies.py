from utils import errors

import shutil
import subprocess


class Checks:
    def __init__(self):
        self.check_bin('futurerestore')
        self.check_bin('tsschecker')
        self.check_bin('irecovery')
        self.check_bin('img4tool')

    def check_bin(self, binary: str) -> None:
        if shutil.which(binary) is None:
            raise errors.DependencyError(f'Binary not found on your PC: {binary}.')

        if binary == 'futurerestore':
            fr_ver = subprocess.run(
                (binary), stdout=subprocess.PIPE, universal_newlines=True
            ).stdout
            if '-m1sta' not in fr_ver.splitlines()[1]:
                raise errors.DependencyError(
                    'This FutureRestore build cannot be used with Inferius.'
                )

        elif binary == 'irecovery':
            try:
                subprocess.check_call(
                    (binary, '-V'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                raise errors.DependencyError(
                    'This iRecovery build is too old to be used with Inferius.'
                ) from None
