import subprocess
import sys
import usb

class Device(object):
    def __init__(self, device_identifier):
        super().__init__()

        self.device = device_identifier
        self.baseband = self.check_baseband()
        self.platform = self.fetch_platform()
        self.boardconfig = self.fetch_boardconfig()
        self.apnonce = self.fetch_apnonce()
        self.ecid = self.fetch_ecid()

    def check_baseband(self):
        if self.device.startswith('iPhone'):
            return True

        elif self.device.startswith('iPod'):
            return False

        elif self.device.startswith('iPad'):
            cellular_ipads = ['iPad4,2', 'iPad4,3', 'iPad5,4', 'iPad11,4', 'iPad13,2', 'iPad6,8', 'iPad6,4', 'iPad7,2', 'iPad7,4', 'iPad8,3', 'iPad8,4', 'iPad8,7', 'iPad8,8', 'iPad8,10', 'iPad8,12', 'iPad4,5', 'iPad4,6', 'iPad4,8', 'iPad4,9', 'iPad5,2', 'iPad11,2']
            if self.device in cellular_ipads:
                return True
            else:
                return False

    def check_pwndfu(self):
        try:
            device = usb.core.find(idVendor=0x5AC, idProduct=0x1227)

        except usb.core.NoBackendError:
            sys.exit('[ERROR] libusb is not installed. Install libusb from Homebrew. Exiting...')

        if device == None:
            sys.exit('[ERROR] Device in DFU mode not found. Exiting...')

        if 'PWND:[checkm8]' not in device.serial_number:
            sys.exit('[ERROR] Attempting to restore a device not in Pwned DFU mode. Exiting...')

    def fetch_boardconfig(self):
        irecovery = subprocess.run(('irecovery', '-qv'), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, universal_newlines=True)

        return irecovery.stderr.splitlines()[4].split(' ')[4][:-1]

    def fetch_apnonce(self):
        irecovery = subprocess.run(('irecovery', '-q'), stdout=subprocess.PIPE, universal_newlines=True)

        return irecovery.stdout.splitlines()[-3].split(' ')[-1]

    def fetch_platform(self):
        try:
            device = usb.core.find(idVendor=0x5AC, idProduct=0x1227)

        except usb.core.NoBackendError:
            sys.exit('[ERROR] libusb is not installed. Install libusb from Homebrew. Exiting...')

        if device == None:
            sys.exit('[ERROR] Device in DFU mode not found. Exiting...')

        return int(device.serial_number.split(' ')[0].split(':')[1])

    def fetch_ecid(self):
        try:
            device = usb.core.find(idVendor=0x5AC, idProduct=0x1227)

        except usb.core.NoBackendError:
            sys.exit('[ERROR] libusb is not installed. Install libusb from Homebrew. Exiting...')

        if device == None:
            sys.exit('[ERROR] Device in DFU mode not found. Exiting...')

        ecid = device.serial_number.split(' ')[5].split(':')[1]

        for x in ecid:
            if x == '0':
                ecid = ecid[1:]
            else:
                break

        return ecid