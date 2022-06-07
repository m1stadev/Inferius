from pathlib import Path
from typing import Optional
from utils import errors, usb

import json


class Device:
    def __init__(self, identifier):
        self.identifier = identifier
        self.data = self._get_data()
        self.board = self.fetch_board()

    def _get_data(self) -> Optional[dict]:
        device = usb.get_device(usb.DFU)

        device_data = dict()
        for item in (
            *device.serial_number.split(),
            *usb.get_string(device, device.bDescriptorType).split(),
        ):
            name, value = item.split(':')
            if name in ('NONC', 'SNON'):
                device_data[name] = bytes.fromhex(value)
            elif value.startswith('[') and value.endswith(']'):
                device_data[name] = value
            else:
                device_data[name] = int(value, 16)

        usb.release_device(device)
        return device_data

    def fetch_board(self) -> Optional[str]:
        device_info = Path('utils/devices.json')
        try:
            with device_info.open('r') as f:
                data = json.load(f)

        except FileNotFoundError:
            raise errors.CorruptError(
                f'File missing from Inferius: {device_info}'
            ) from None

        return next(
            _['boardconfig']
            for _ in data
            if _['identifier'] == self.identifier
            and _['bdid'] == self.data['BDID']
            and _['cpid'] == self.data['CPID']
        )
