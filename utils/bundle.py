from pathlib import Path
from remotezip import RemoteZip, RemoteIOError
from typing import Optional
from utils import errors

import bsdiff4
import json
import zipfile


class Bundle:
    def __init__(self, bundle: Optional[Path] = None):
        self.bundle = bundle

    def apply_patches(self, ipsw: Path) -> None:
        with (self.bundle / 'Info.json').open('r') as f:
            bundle_data = json.load(f)

        for patches in bundle_data['patches']:
            if patches != 'required':
                apply_patch = input(
                    f"[NOTE] Would you like to apply '{patches}' patch to your custom IPSW? [Y/N]: "
                ).lower()
                if apply_patch == 'n':
                    continue

                elif apply_patch not in ('y', 'n'):
                    print('[WARN] Invalid input, skipping patch...')
                    continue

            for patch in bundle_data['patches'][patches]:
                bsdiff4.file_patch_inplace(
                    ipsw / patch['file'], self.bundle / patch['patch']
                )

    def check_update_support(self) -> bool:
        with (self.bundle / 'Info.json').open('r') as f:
            bundle_data = json.load(f)

        return bundle_data['update_support']

    def fetch_bundle(
        self, device: str, version: tuple, buildid: str, path: Path
    ) -> None:
        bundle_name = '_'.join([device, '.'.join([str(_) for _ in version]), buildid])

        bundle = path / bundle_name
        bundle.mkdir()

        try:
            with RemoteZip(
                f'https://github.com/m1stadev/inferius-ext/raw/master/bundles/{bundle_name}.bundle'
            ) as rz:
                try:
                    rz.extractall(bundle)
                except OSError:
                    raise IOError(
                        f'Failed to download firmware bundle to: {bundle}.'
                    ) from None

        except RemoteIOError:
            raise errors.NotFoundError(
                f"A firmware bundle does not exist for device: {device}, OS: {'.'.join([str(_) for _ in version])}."
            ) from None

        self.bundle = bundle

    def verify_bundle(
        self, path: Path, api: dict, buildid: str, boardconfig: str
    ) -> None:
        if not self.bundle.exists():
            raise errors.NotFoundError(
                f'Firmware bundle does not exist: {self.bundle}.'
            )

        if not zipfile.is_zipfile(self.bundle):
            raise errors.CorruptError(f'Firmware bundle is corrupt: {self.bundle}.')

        if not any(_['buildid'] == buildid for _ in api['firmwares']):
            return

        try:
            with zipfile.ZipFile(self.bundle, 'r') as f:
                bundle_data = json.loads(f.read('Info.json'))

            next(_.lower() == boardconfig.lower() for _ in bundle_data['boards'])

        except StopIteration:
            return

        bundle = path / self.bundle.stem
        bundle.mkdir()

        with zipfile.ZipFile(self.bundle) as f:
            f.extractall(bundle)

        self.bundle = bundle
