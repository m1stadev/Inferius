from utils import errors

import shutil
import subprocess


class Checks:
    def __init__(self):
        self.check_bin("futurerestore")
        self.check_bin("tsschecker")
        self.check_bin("irecovery")
        self.check_bin("img4tool")

    def check_bin(self, binary: str) -> None:
        if shutil.which(binary) is None:
            raise errors.DependencyError(f"Binary not found on your PC: {binary}.")

        if binary == "futurerestore":
            fr_help = subprocess.check_output(
                (binary, "--help"), stderr=subprocess.DEVNULL, universal_newlines=True
            )

            if (
                "--skip-blob" not in fr_help
            ):  # Inferius relies on the '--skip-blob' option
                raise errors.DependencyError(
                    "This FutureRestore build is too old be used with Inferius."
                )

        elif binary == "irecovery":
            try:
                subprocess.check_call(
                    (binary, "-V"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                raise errors.DependencyError(
                    "This iRecovery build is too old to be used with Inferius."
                ) from None
