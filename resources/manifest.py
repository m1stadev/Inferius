import plistlib

class Manifest(object):
    def __init__(self, manifest, boardconfig):
        super().__init__()

        self.manifest = plistlib.load(manifest)
        self.boardconfig = boardconfig
        self.version = self.fetch_version()
        self.buildid = self.fetch_buildid()

    def fetch_version(self): return self.manifest['ProductVersion']

    def fetch_buildid(self): return self.manifest['ProductBuildVersion']

class RestoreManifest(object):
    def __init__(self, manifest, device, boardconfig):
        super().__init__()

        self.device = device
        self.manifest = plistlib.load(manifest)
        self.boardconfig = boardconfig
        self.platform = self.fetch_platform()

    def fetch_platform(self):
        for x in range(0, len(self.manifest['DeviceMap'])):
            if self.manifest['DeviceMap'][x]['BoardConfig'] == self.boardconfig:

                if self.manifest['DeviceMap'][x]['Platform'].startswith('s5l89'):
                    return int(self.manifest['DeviceMap'][x]['Platform'][3:-1])

                else:
                    return int(self.manifest['DeviceMap'][x]['Platform'][-4:])