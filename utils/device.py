import glob
import os
import subprocess
import sys
import usb, usb.backend.libusb1


class Device(object):
	def __init__(self, identifier):
		self.device = identifier
		self.baseband = self.check_baseband()
		self.backend = self.get_backend()
		self.platform = self.fetch_platform()
		self.board = self.fetch_boardconfig()
		self.apnonce = self.fetch_apnonce()
		self.ecid = self.fetch_ecid()

	def check_baseband(self):
		if self.device.startswith('iPhone'):
			return True

		cellular_ipads = [ # All (current) 64-bit cellular iPads vulerable to checkm8.
			'iPad4,2',
			'iPad4,3',
			'iPad4,5',
			'iPad4,6',
			'iPad4,8',
			'iPad4,9',
			'iPad5,2',
			'iPad5,4',
			'iPad6,8',
			'iPad6,4',
			'iPad7,2',
			'iPad7,4',
			'iPad8,3',
			'iPad8,4',
			'iPad8,7',
			'iPad8,8',
			'iPad8,10',
			'iPad8,12',
			'iPad11,2'
			'iPad11,4',
			'iPad13,2',
			]

		return self.device in cellular_ipads

	def check_pwndfu(self):
		device = usb.core.find(idVendor=0x5AC, idProduct=0x1227, backend=self.backend)
		if device is None:
			sys.exit('[ERROR] Device in DFU mode not found. Exiting.')

		if 'PWND:' not in device.serial_number:
			sys.exit('[ERROR] Attempting to restore a device not in Pwned DFU mode. Exiting.')

	def fetch_apnonce(self):
		irecv = subprocess.check_output(('irecovery', '-q'), universal_newlines=True)
		line = next(l for l in irecv.splitlines() if 'NONC:' in l)
		return line.split(' ')[1]

	def get_backend(self): # Attempt to find a libusb 1.0 library to use as pyusb's backend, exit if one isn't found.
		directories = ('/usr/lib', '/opt/procursus/lib', '/usr/local/lib') # Common library directories to search

		libusb1 = None
		for libdir in directories:
			for file in glob.glob(libdir + '/**', recursive=True):
				if os.path.isdir(file) or (not any(ext in file for ext in ('so', 'dylib'))):
					continue

				if 'libusb-1.0' in file:
					libusb1 = file
					break

			else:
				continue

			break

		if libusb1 is None:
			sys.exit('[ERROR] libusb is not installed. Install libusb. Exiting.')

		return usb.backend.libusb1.get_backend(find_library=lambda x:libusb1)

	def fetch_boardconfig(self):
		irecovery = subprocess.run(('irecovery', '-qv'), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, universal_newlines=True).stderr
		return irecovery.splitlines()[4].split(', ')[1].replace('model ', '')

	def fetch_ecid(self):
		device = usb.core.find(idVendor=0x5AC, idProduct=0x1227, backend=self.backend)
		if device is None:
			sys.exit('[ERROR] Device in DFU mode not found. Exiting.')

		ecid = device.serial_number.split(' ')[5].split(':')[1]

		for x in ecid:
			if x == '0':
				ecid = ecid[1:]
			else:
				break

		return ecid

	def fetch_platform(self):
		device = usb.core.find(idVendor=0x5AC, idProduct=0x1227, backend=self.backend)
		if device is None:
			sys.exit('[ERROR] Device in DFU mode not found. Exiting.')

		return int(device.serial_number.split(' ')[0].split(':')[1])
