from pathlib import Path
from typing import Optional
from utils.api import API
from utils import errors

import hashlib
import json
import shutil
import zipfile


class IPSW:
    def __init__(self, ipsw: Path):
        self.ipsw = ipsw

    def __str__(self) -> str:
        return str(self.ipsw)

    def create_ipsw(
        self, path: Path, filename: str, update: bool, bootloader: str
    ) -> Optional[Path]:
        ipsw = Path(f'IPSW/{filename}')
        ipsw.parent.mkdir(exist_ok=True)

        info = {'update_support': update, 'bootloader': bootloader}

        with (Path / '.Inferius').open('w') as f:
            json.dump(info, f)

        try:
            shutil.make_archive(ipsw, 'zip', path)
        except:
            raise OSError(f'Failed to create custom IPSW at path: {ipsw}.')

        return ipsw.rename(ipsw.with_suffix('.ipsw'))

    def extract_file(self, file: str, output: Path) -> Path:
        try:
            with zipfile.ZipFile(self.ipsw, 'r') as ipsw, (output / file).open(
                'wb'
            ) as f:
                f.write(ipsw.read(file))

        except KeyError as e:
            raise errors.NotFoundError(f'File not in IPSW: {file}.') from e

        except OSError as e:
            raise IOError(f'Failed to extract file from IPSW: {file}.')

    def extract_ipsw(self, path: Path) -> None:
        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            try:
                ipsw.extractall(path)
            except OSError as e:
                raise OSError(f'Failed to extract IPSW: {self.ipsw}.') from e

    def read_file(self, file: str) -> Optional[bytes]:
        try:
            with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
                return ipsw.read(file)

        except KeyError as e:
            raise errors.NotFoundError(f'File not in IPSW: {file}.') from e

    def verify_ipsw(self, sha1: str) -> None:
        if not self.ipsw.is_file():
            raise errors.NotFoundError(f'IPSW does not exist: {self.ipsw}.')

        if not zipfile.is_zipfile(self.ipsw):
            raise errors.BadIPSWError(f'IPSW is corrupt: {self.ipsw}.')

        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            if '.Inferius' in ipsw.namelist():
                raise errors.BadIPSWError(f'IPSW has been modified: {self.ipsw}.')

        hash = hashlib.sha1()
        with self.ipsw.open('rb') as ipsw:
            fbuf = ipsw.read(65536)
            while len(fbuf) > 0:
                hash.update(fbuf)
                fbuf = ipsw.read(65536)

        if sha1 != hash.hexdigest():
            raise errors.BadIPSWError(f'IPSW is corrupt: {self.ipsw}.')

    def verify_custom_ipsw(self, api: API, update: bool) -> None:
        if not self.ipsw.is_file():
            raise errors.NotFoundError(f'IPSW does not exist: {self.ipsw}.')

        if not zipfile.is_zipfile(self.ipsw):
            raise errors.BadIPSWError(f'IPSW is corrupt: {self.ipsw}.')

        with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
            if '.Inferius' not in ipsw.namelist():
                raise errors.BadIPSWError(f'IPSW is not custom: {self.ipsw}.')

            info = json.loads(ipsw.read('.Inferius'))

        if (info['update_support'] == False) and (update == True):
            raise errors.BadIPSWError(
                f'IPSW does not support update restores: {self.ipsw}.'
            )

        if api.is_signed(info['bootloader']) == False:
            raise errors.BadIPSWError(
                f'IPSW is too old to be used with Inferius: {self.ipsw}. A new custom IPSW must be created.'
            )
