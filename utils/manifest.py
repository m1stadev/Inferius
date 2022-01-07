import plistlib


class Manifest:
    def __init__(self, manifest):
        self.manifest = plistlib.loads(manifest)
        self.version = (int(_) for _ in self.manifest['ProductVersion'].split('.'))
        self.buildid = self.manifest['ProductBuildVersion']
        self.supported_devices = self.manifest['SupportedProductTypes']

    def fetch_component_path(self, boardconfig: str, component: str) -> str:
        return next(identity['Manifest'][component]['Info']['Path'] for identity in self.manifest['BuildIdentities'] if identity['Info']['DeviceClass'].lower() == boardconfig.lower())

class RestoreManifest:
    def __init__(self, manifest, boardconfig):
        self.platform = self.fetch_platform(boardconfig, plistlib.loads(manifest))

    def fetch_platform(self, boardconfig, manifest):
        for device in manifest['DeviceMap']:
            if device['BoardConfig'].lower() != boardconfig.lower():
                continue

            if device['Platform'].startswith('s5l89'):
                return int(device['Platform'][3:-1], 16)

            else:
                return int(device['Platform'][-4:], 16)
