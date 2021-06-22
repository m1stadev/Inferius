import plistlib


class Manifest(object):
	def __init__(self, manifest):
		self.manifest = plistlib.loads(manifest)
		self.version = self.fetch_version()
		self.buildid = self.fetch_buildid()
		self.supported_devices = self.fetch_supported_devices()

	def fetch_buildid(self): return self.manifest['ProductBuildVersion']

	def fetch_component_path(self, boardconfig, component):
		return next(identity['Manifest'][component]['Info']['Path'] for identity in self.manifest['BuildIdentities'] if identity['Info']['DeviceClass'].lower() == boardconfig.lower())

	def fetch_supported_devices(self): return self.manifest['SupportedProductTypes']

	def fetch_version(self): return self.manifest['ProductVersion']

class RestoreManifest(object):
	def __init__(self, manifest, boardconfig):
		self.platform = self.fetch_platform(boardconfig, plistlib.loads(manifest))

	def fetch_platform(self, boardconfig, manifest):
		for device in manifest['DeviceMap']:
			if device['BoardConfig'].lower() != boardconfig.lower():
				continue

			if device['Platform'].startswith('s5l89'):
				return int(device['Platform'][3:-1])

			else:
				return int(device['Platform'][-4:])
