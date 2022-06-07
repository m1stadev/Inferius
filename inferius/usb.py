from pathlib import Path
from typing import Optional
from utils import errors

import usb, usb.backend.libusb1, usb.util


RECOVERY = 0x1281
DFU = 0x1227


def _get_backend() -> Optional[
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
            if not file.is_file() or (file.suffix not in ('.so', '.dylib')):
                continue

            libusb1 = file
            break

        else:
            continue

        break

    if libusb1 is None:
        raise errors.DependencyError('libusb not found on your PC.')

    return usb.backend.libusb1.get_backend(find_library=lambda _: libusb1)


def get_device(mode: int) -> Optional[usb.core.Device]:
    if mode not in (DFU, RECOVERY):
        raise errors.DeviceError(f'Invalid mode specified: {mode}.')

    device: usb.core.Device = usb.core.find(
        idVendor=0x5AC, idProduct=mode, backend=_get_backend()
    )

    if device is None:
        raise errors.DeviceError(f'Device not found.')

    return device


def get_string(device: usb.core.Device, index: int) -> Optional[str]:
    return usb.util.get_string(device, index)


def send_cmd(device: usb.core.Device, cmd: str) -> None:
    if device.idProduct != RECOVERY:
        raise errors.DeviceError(
            'Commands can only be send to a device in Recovery mode.'
        )

    device.ctrl_transfer(0x40, 1, 0, 0, cmd)


def release_device(device: usb.core.Device) -> None:
    usb.util.dispose_resources(device)


def reset_device(device: usb.core.Device) -> None:
    device.reset()
