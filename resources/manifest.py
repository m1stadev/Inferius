import plistlib

class Manifest(object):
	def __init__(self, manifest):
		super().__init__()

		self.manifest = plistlib.load(manifest)
		self.version = self.fetch_version()
		self.buildid = self.fetch_buildid()
		self.supported_devices = self.fetch_supported_devices()

	def fetch_version(self): return self.manifest['ProductVersion']

	def fetch_buildid(self): return self.manifest['ProductBuildVersion']

	def fetch_supported_devices(self): return self.manifest['SupportedProductTypes']

	def fetch_component_path(self, boardconfig, component): return next(self.manifest['BuildIdentities'][x]['Manifest'][component]['Info']['Path'] for x in range(len(self.manifest['BuildIdentities'])) if self.manifest['BuildIdentities'][x]['Info']['DeviceClass'] in boardconfig)

class RestoreManifest(object):
	def __init__(self, manifest, device, boardconfig):
		super().__init__()

		self.device = device
		self.boardconfig = boardconfig
		self.manifest = plistlib.load(manifest)
		self.platform = self.fetch_platform()

	def fetch_platform(self):
		for x in range(len(self.manifest['DeviceMap'])):
			if self.manifest['DeviceMap'][x]['BoardConfig'] in self.boardconfig:

				if self.manifest['DeviceMap'][x]['Platform'].startswith('s5l89'):
					return int(self.manifest['DeviceMap'][x]['Platform'][3:-1])

				else:
					return int(self.manifest['DeviceMap'][x]['Platform'][-4:])
