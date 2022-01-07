from pathlib import Path
from typing import Optional
from utils import errors

import remotezip
import requests


class API:
    def __init__(self, identifier: str) -> None:
        self.device = identifier
        self.api = self.fetch_api()
        self.board = self.get_board()

    def is_signed(self, version: str) -> bool: return any(firm['signed'] == True for firm in self.api['firmwares'] if firm['version'] == version)

    def check_version(self, version) -> Optional[bool]:
        if not any(firm['version'] == version for firm in self.api['firmwares']):
            raise errors.NotFoundError(f"Version does not exist: {version}.")

        return True

    def fetch_api(self) -> Optional[dict]:
        try:
            return requests.get(f'https://api.ipsw.me/v4/device/{self.device}').json()
        except requests.exceptions.JSONDecodeError:
            raise errors.NotFoundError(f"Device does not exist: {self.device}.")

    def fetch_board(self) -> Optional[str]:
        boards = [board['boardconfig'].lower() for board in self.api['boards'] if board['boardconfig'].lower().endswith('ap')]
        if len(boards) == 1:
            return boards[0]

        else:
            print('There are multiple board configs for your device! Please choose the correct boardc onfig for your device:')
            for b in range(len(boards)):
                print(f"  {b + 1}: {boards[b]}")

            board = input('Choice: ')
            try:
                board = int(board) - 1
            except:
                raise TypeError(f'Invalid choice given: {board}.')
            else:
                if board not in range(len(boards)):
                    raise ValueError(f'Incorrect choice given: {board}.')

            return boards[board]

    def fetch_sha1(self, buildid: str) -> str:
        return next(firm['sha1sum'] for firm in self.api['firmwares'] if firm['buildid'] == buildid)

    def partialzip_extract(self, buildid: str, component: str, path: Path) -> Optional[Path]:
        try:
            firm = next(firm for firm in self.api['firmwares'] if firm['buildid'] == buildid)
        except StopIteration:
            raise errors.NotFoundError(f'Buildid does not exist: {buildid}.')

        with remotezip.RemoteZip(firm['url']) as ipsw:
            try:
                ipsw.extract(component, path)
            except KeyError:
                raise errors.NotFoundError(f'Component does not exist: {component}.')
            except OSError:
                raise OSError(f'Failed to partialzip component: {component}.')

        return path / Path(component)

    def partialzip_read(self, buildid: str, component: str) -> Optional[bytes]:
        try:
            firm = next(firm for firm in self.api['firmwares'] if firm['buildid'] == buildid)
        except StopIteration:
            raise errors.NotFoundError(f'Buildid does not exist: {buildid}.')

        with remotezip.RemoteZip(firm['url']) as ipsw:
            try:
                return ipsw.read(component)
            except KeyError:
                raise errors.NotFoundError(f'Component does not exist: {component}.')
