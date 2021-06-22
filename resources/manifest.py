import plistlib


class Manifest(object):
	def __init__(self, manifest):
		self.manifest = plistlib.load(manifest)
		self.version = self.fetch_version()
		self.buildid = self.fetch_buildid()
		self.supported_devices = self.fetch_supported_devices()

	def fetch_version(self): return self.manifest['ProductVersion']

	def fetch_buildid(self): return self.manifest['ProductBuildVersion']

	def fetch_supported_devices(self): return self.manifest['SupportedProductTypes']

	def fetch_component_path(self, boards, component):
		return next(identity['Manifest'][component]['Info']['Path'] for identity in self.manifest['BuildIdentities'] if identity['Info']['DeviceClass'] in boards)


class RestoreManifest(object):
	def __init__(self, identifier, manifest, boards):
		self.device = identifier
		self.boards = boards
		self.manifest = plistlib.load(manifest)
		self.platform = self.fetch_platform()

	def fetch_platform(self):
		for device in self.manifest['DeviceMap']:
			if device['BoardConfig'] in self.boards:
				if device['Platform'].startswith('s5l89'):
					return int(device['Platform'][3:-1])

				else:
					return int(device['Platform'][-4:])
