from pathlib import Path
from typing import Optional
from utils import errors, usb

import json


class Device:
    def __init__(self, identifier):
        self.identifier = identifier
        self.data = self._get_dfu_data()
        self.board = self.fetch_board()

    def _get_dfu_data(self) -> Optional[dict]:
        device = usb.get_device(usb.DFU)

        device_data = dict()
        for item in device.serial_number.split():
            device_data[item.split(':')[0]] = item.split(':')[1]

        device_data['ECID'] = hex(int(device_data['ECID'], 16))

        for i in ('CPID', 'CPRV', 'BDID', 'CPFM', 'SCEP', 'IBFL'):
            device_data[i] = int(device_data[i], 16)

        for item in usb.get_string(device, device.bDescriptorType).split():
            device_data[item.split(':')[0]] = item.split(':')[1]

        usb.release_device(device)
        return device_data

    @property
    def baseband(self) -> bool:
        if self.identifier.startswith('iPhone'):
            return True

        else:
            return (
                self.identifier
                in (  # All (current) 64-bit cellular iPads vulerable to checkm8.
                    'iPad4,2',
                    'iPad4,3',
                    'iPad4,5',
                    'iPad4,6',
                    'iPad4,8',
                    'iPad4,9',
                    'iPad5,2',
                    'iPad5,4',
                    'iPad6,4',
                    'iPad6,8',
                    'iPad6,12',
                    'iPad7,2',
                    'iPad7,4',
                    'iPad7,6',
                    'iPad7,12',
                )
            )

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
