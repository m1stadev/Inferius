from pathlib import Path
from typing import Optional
from utils import errors

import json
import usb, usb.backend.libusb1, usb.util


class Device:
    def __init__(self, identifier):
        self.identifier = identifier
        self.board = self.fetch_boardconfig()
        self.data = self._get_dfu_data()

    def _get_dfu_data(self) -> Optional[dict]:
        device: usb.core.Device = usb.core.find(
            idVendor=0x5AC, idProduct=0x1227, backend=self.get_backend()
        )
        if device is None:
            raise errors.DeviceError('Device in DFU mode not found.')

        device_data = dict()
        for item in device.serial_number.split():
            device_data[item.split(':')[0]] = item.split(':')[1]

        device_data['ECID'] = hex(int(device_data['ECID'], 16))

        for i in ('CPID', 'CPRV', 'BDID', 'CPFM', 'SCEP', 'IBFL'):
            device_data[i] = int(device_data[i], 16)

        for item in usb.util.get_string(device, device.bDescriptorType).split():
            device_data[item.split(':')[0]] = item.split(':')[1]

        usb.util.dispose_resources(device)

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

    def get_backend(
        self,
    ) -> Optional[
        usb.backend.libusb1._LibUSB
    ]:  # Attempt to find a libusb 1.0 library to use as pyusb's backend, exit if one isn't found.
        directories = (
            '/usr/local/lib',
            '/opt/procursus/lib',
            '/usr/lib',
        )  # Common library directories to search

        libusb1 = None
        for libdir in directories:
            for file in Path(libdir).glob('libusb-1.0.0.*'):
                if file.is_dir() or (file.suffix not in ('.so', '.dylib')):
                    continue

                libusb1 = file
                break

            else:
                continue

            break

        if libusb1 is None:
            raise errors.DependencyError('libusb not found on your PC.')

        return usb.backend.libusb1.get_backend(find_library=lambda _: libusb1)

    def fetch_board(self) -> Optional[str]:
        device_info = Path('utils/devices.json')
        try:
            with device_info.open('r') as f:
                data = json.load(f)

        except FileNotFoundError as e:
            raise errors.CorruptError(
                f'File missing from Inferius: {device_info}'
            ) from e

        return next(
            _['boardconfig']
            for _ in data
            if _['identifier'] == self.identifier
            and _['bdid'] == self.data['BDID']
            and _['cpid'] == self.data['CPID']
        )
