from pathlib import Path
from remotezip import RemoteZip, RemoteIOError
from typing import Optional
from utils.api import API
from utils import errors

import bsdiff4
import json
import requests
import zipfile


class Bundle:
    def apply_patches(self, ipsw: Path) -> None:
        with (self.bundle / 'Info.json').open('r') as f:
            bundle_data = json.load(f)

        for patches in bundle_data['patches']:
            if patches != 'required':
                apply_patch = input(f"[NOTE] Would you like to apply '{patches}' patch to your custom IPSW? [Y\\N]: ").lower()
                if (apply_patch not in ('y', 'n')) or (apply_patch == 'n'):
                    continue

            for patch in bundle_data['patches'][patches]:
                bsdiff4.file_patch_inplace(ipsw / patch['file'], self.bundle / patch['patch'])

    def check_update_support(self):
        with (self.bundle / 'Info.json').open('r') as f:
            bundle_data = json.load(f)

        return bundle_data['update_support']

    def fetch_bundle(self, device: str, version: tuple, buildid: str, path: Path) -> Optional[Path]:
        bundle_name = '_'.join(device, '.'.join(version), buildid)

        bundle = path / bundle_name
        bundle.mkdir()

        try:
            with RemoteZip(f'https://github.com/m1stadev/inferius-ext/raw/master/bundles/{bundle_name}.bundle') as rz:
                try:
                    rz.extractall(bundle)
                except OSError:
                    raise OSError(f'Failed to extract Firmware Bundle to: {bundle}.')

        except RemoteIOError:
            raise errors.NotFoundError(f'A bundle does not exist for device: {device}, OS: {version}.')

        return bundle

    def fetch_ota_manifest(self, device: str, path: Path) -> Optional[Path]:
        r = requests.get(f'https://github.com/m1stadev/inferius-ext/raw/master/manifests/BuildManifest_{device}.plist')
        if r.status_code == 404:
            raise errors.NotFoundError(f'An OTA manifest does not exist for device: {device}.')

        manifest = path / 'otamanifest.plist'
        with manifest.open('wb') as f:
            try:
                f.write(r.content)
            except OSError:
                raise OSError(f'Failed to write OTA manifest to: {manifest}.')

        return manifest

    def verify_bundle(self, local_bundle: Path, path: Path, api: API, buildid: str, boardconfig: str) -> Optional[Path]:
        if not zipfile.is_zipfile(local_bundle):
            return

        try:
            with zipfile.ZipFile(local_bundle, 'r') as f:
                try:
                    bundle_data = json.loads(f.read('Info.json'))
                except:
                    return

            if not any(firm['buildid'] == buildid for firm in api['firmwares']):
                return

            if not any(board.lower() == boardconfig.lower() for board in bundle_data['boards']):
                return

        except:
            return

        bundle = path / local_bundle.stem
        bundle.mkdir()

        with zipfile.ZipFile(local_bundle) as f:
            f.extractall(bundle)

        return bundle
