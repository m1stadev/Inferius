from pathlib import Path
from typing import Optional
from utils import errors

import usb, usb.backend.libusb1, usb.util


def _get_backend(
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

def get_device(self) -> Optional[usb.core.Device]:
    device: usb.core.Device = usb.core.find(
        idVendor=0x5AC, idProduct=0x1227, backend=_get_backend()
    )
    if device is None:
        raise errors.DeviceError('Device in DFU mode not found.')

    return

def get_string(self, device: usb.core.Device, index: int) -> Optional[str]:
    return usb.util.get_string(device, index)

def release_device(self, device: usb.core.Device) -> None:
    usb.util.dispose_resources(device)

def reset_device(self, device: usb.core.Device) -> None:
    device.reset()
