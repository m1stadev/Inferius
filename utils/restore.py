from pathlib import Path
from utils.device import Device
from utils import errors, usb

import shutil
import subprocess
import time


class Restore:
    def __init__(self, device: Device):
        self.device = device

    def _irecv_send_file(self, file: Path) -> None:
        try:
            subprocess.check_call(
                ('irecovery', '-f', file), stdout=subprocess.DEVNULL
            )
        except:
            raise errors.RestoreError(f"Failed to send file to device: {file}.")

    def _irecv_send_cmd(self, cmd: str) -> None:
        try:
            subprocess.check_call(
                ('irecovery', '-c', cmd), stdout=subprocess.DEVNULL
            )
        except:
            raise errors.RestoreError(f"Failed to send command to device: '{cmd}'.")

    def restore(self, ipsw: Path, cellular: bool, update: bool, *, sep: Path=None, manifest: Path=None) -> None:
        args = ['futurerestore', '-t', self.blob]

        if sep and manifest:
            args.append('-s')
            args.append(sep)

            args.append('-m')
            args.append(manifest)

        else:
            args.append('--latest-sep')

        if cellular:
            args.append('--latest-baseband')
        else:
            args.append('--no-baseband')

        if update:
            args.append('-u')

        args.append(ipsw)

        Path('restore.log').unlink(missing_ok=True)
        try:
            futurerestore = subprocess.check_output(
                args, stderr=subprocess.STDOUT, universal_newlines=True
            )

        except subprocess.CalledProcessError as process:
            with open('restore.log', 'w') as f:
                f.write(f"{' '.join(args)}\n\n")
                f.write(process.stdout)

        if Path(ipsw.stem).is_dir():
            shutil.rmtree(ipsw.stem)

        if 'Done: restoring succeeded!' not in futurerestore.stdout:
            with open('restore.log', 'w') as f:
                f.write(f"{' '.join(args)}\n\n")
                f.write(process.stdout)

            raise errors.RestoreError(
                "[ERROR] Restore failed. Log written to 'restore.log'. Exiting."
            )

    def save_blobs(self, ecid: str, boardconfig: str, path: Path, *, manifest: Path=None, apnonce: str=None) -> None:
        args = [
            'tsschecker',
            '-d', self.device.identifier,
            '-B', boardconfig,
            '-e', ecid,
            '--save-path', path,
            '-s',
        ]

        if manifest:
            args.append('-m')
            args.append(manifest)
        else:
            args.append('-l')
            args.append('--nocache')

        if apnonce:
            args.append('--apnonce')
            args.append(apnonce)

        tsschecker = subprocess.check_output(args, universal_newlines=True)
        if 'Saved shsh blobs!' not in tsschecker:
            raise errors.RestoreError('Failed to save SHSH blobs.')

        if apnonce:
            for blob in path.glob('*.shsh*'):
                if blob != self.signing_blob:
                    self.blob = blob
                    break
        else:
            self.signing_blob = path.glob('*.shsh*')[0]

    def send_bootchain(self, ibss: Path, ibec: Path) -> None:
        # Reset device
        device = usb.get_device()
        usb.reset_device(device)
        usb.release_device(device)

        self._irecv_send_file(ibss)
        self._irecv_send_file(ibec)

        if 0x8010 <= self.device.data['CPID'] <= 0x8015:
            self._irecv_send_cmd('go')
            time.sleep(3)

    def sign_component(self, file: Path, output: Path) -> None:
        args = ('img4tool', '-c', output, '-p', file, '-s', self.signing_blob)

        try:
            subprocess.check_call(args, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            raise errors.RestoreError(f"Failed to sign component: {file}.")
