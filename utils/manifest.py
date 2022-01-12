from typing import Optional

import plistlib


class Manifest:
    def __init__(self, manifest: bytes):
        self._manifest = plistlib.loads(manifest)
        self.version = (int(_) for _ in self._manifest['ProductVersion'].split('.'))
        self.buildid = self._manifest['ProductBuildVersion']
        self.supported_devices = self._manifest['SupportedProductTypes']

    def fetch_component_path(self, boardconfig: str, component: str) -> str:
        return next(
            identity['Manifest'][component]['Info']['Path']
            for identity in self.manifest['BuildIdentities']
            if identity['Info']['DeviceClass'].lower() == boardconfig.lower()
        )


class RestoreManifest:
    def __init__(self, manifest: bytes, boardconfig: str):
        self._manifest = plistlib.loads(manifest)
        self.boardconfig = boardconfig

    @property
    def platform(self) -> Optional[int]:
        for device in self._manifest['DeviceMap']:
            if device['BoardConfig'].lower() != self.boardconfig.lower():
                continue

            if device['Platform'].startswith('s5l89'):
                return int(device['Platform'][3:-1], 16)

            else:
                return int(device['Platform'][-4:], 16)
