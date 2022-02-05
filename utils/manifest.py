from typing import Optional
from utils import errors

import plistlib


class Manifest:
    def __init__(self, manifest: bytes, board: str):
        self._manifest = plistlib.loads(manifest)

        self.version = tuple(
            int(_) for _ in self._manifest['ProductVersion'].split('.')
        )
        self.buildid = self._manifest['ProductBuildVersion']
        self.supported_devices = self._manifest['SupportedProductTypes']

        # Get proper capitalization for board
        self.board = next(
            _['Info']['DeviceClass']
            for _ in self._manifest['BuildIdentities']
            if _['Info']['DeviceClass'].lower() == board.lower()
        )

        self.id = next(
            _
            for _ in range(len(self._manifest['BuildIdentities']))
            if self._manifest['BuildIdentities'][_]['Info']['DeviceClass'] == self.board
        )

    def get_path(self, component: str) -> str:
        if (
            component
            not in self._manifest['BuildIdentities'][self.id]['Manifest'].keys()
        ):
            raise errors.NotFoundError(f'Component not found in manifest: {component}.')

        return self._manifest['BuildIdentities'][self.id]['Manifest'][component][
            'Info'
        ]['Path']

    def dump(self) -> bytes:
        return plistlib.dumps(self._manifest)


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
