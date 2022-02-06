from pathlib import Path
from utils.device import Device
from utils import errors

import shutil
import subprocess


class Restore:
    def __init__(self, device: Device):
        self.device = device

    def restore(
        self,
        ipsw: Path,
        rdsk: Path,
        kern: Path,
        cellular: bool,
        update: bool,
        *,
        sep: Path = None,
        manifest: Path = None,
    ) -> None:
        args = [
            'futurerestore',
            '-t',
            str(self.signing_blob),
            '--use-pwndfu',
            '--no-cache',
            '--skip-blob',
            '--rdsk',
            str(rdsk),
            '--rkrn',
            str(kern),
        ]

        if sep and manifest:
            args.append('-s')
            args.append(str(sep))

            args.append('-m')
            args.append(str(manifest))

        else:
            args.append('--latest-sep')

        if cellular:
            args.append('--latest-baseband')
        else:
            args.append('--no-baseband')

        if update:
            args.append('-u')

        args.append(str(ipsw))

        log = Path('restore.log')
        log.unlink(missing_ok=True)

        try:
            futurerestore = subprocess.check_output(
                args,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

        except subprocess.CalledProcessError as process:
            with log.open('w') as f:
                f.write(f"{' '.join([_ for _ in args])}\n\n")
                f.write(process.stdout)

            raise errors.RestoreError(
                f"[ERROR] Restore failed. Log written to '{log.stem}'. Exiting."
            ) from None

        if Path(ipsw.stem).is_dir():
            shutil.rmtree(ipsw.stem)

        if 'Done: restoring succeeded!' not in futurerestore:
            with log.open('w') as f:
                f.write(f"{' '.join([_ for _ in args])}\n\n")
                f.write(futurerestore)

            raise errors.RestoreError(
                f"[ERROR] Restore failed. Log written to '{log.stem}'. Exiting."
            )

    def save_blobs(
        self,
        ecid: str,
        boardconfig: str,
        path: Path,
        *,
        manifest: Path = None,
        apnonce: str = None,
    ) -> None:
        args = [
            'tsschecker',
            '-d',
            self.device.identifier,
            '-B',
            boardconfig,
            '-e',
            ecid,
            '--save-path',
            str(path),
            '-s',
        ]

        if manifest:
            args.append('-m')
            args.append(str(manifest))
        else:
            args.append('-l')
            args.append('--nocache')

        if apnonce:
            args.append('--apnonce')
            args.append(apnonce)

        try:
            if 'Saved shsh blobs!' not in subprocess.check_output(
                args, stderr=subprocess.STDOUT, universal_newlines=True
            ):
                raise errors.RestoreError('Failed to save SHSH blobs.')
        except subprocess.CalledProcessError:
            raise errors.RestoreError('Failed to save SHSH blobs.') from None

        if apnonce:
            for blob in path.glob('*.shsh*'):
                if blob != self.signing_blob:
                    self.blob = blob
                    break
        else:
            self.signing_blob = tuple(path.glob('*.shsh*'))[0]

    def sign_image(self, image: Path, output: Path, tag: str = None) -> None:
        args = [
            'img4tool',
            '-c',
            str(output),
            '-p',
            str(image),
            '-s',
            str(self.signing_blob),
        ]

        if tag:
            if len(tag) != 4:
                raise errors.RestoreError(f'Invalid IMG4 tag: {tag}.')

            args.append('-t')
            args.append(tag.lower())

        try:
            subprocess.check_call(args, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            raise errors.RestoreError(f'Failed to sign image: {image}.') from None
