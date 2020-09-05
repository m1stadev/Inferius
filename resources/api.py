import json
import os
import plistlib
import shutil
from urllib.request import urlopen

from remotezip import RemoteZip


class Manifest(object):
    def __init__(self, manifest):
        super().__init__()

        self.data = plistlib.loads(manifest)
        self.device = self.data['SupportedProductTypes'][0]
        self.version = self.data['ProductVersion']
        self.buildid = self.data['ProductBuildVersion']
        self.chipid = self.data['BuildIdentities'][0]['ApChipID']
        self.deviceclass = self.data['BuildIdentities'][0]['Info']['DeviceClass']

        self.paths = list()

        for stuff in self.data['BuildIdentities'][0]['Manifest'].items():
            name = stuff[0]
            path = stuff[1]['Info']['Path']
            self.paths.append({name: path})

    def returnInfo(self):
        info = {
            'data': self.data,
            'device': self.device,
            'version': self.version,
            'buildid': self.buildid,
            'chipid': self.chipid,
            'deviceclass': self.deviceclass,
            'paths': self.paths
        }

        return info


class API(object):
    def __init__(self, device, version=None, buildid=None):
        super().__init__()

        self.device = device
        self.version = version
        self.buildid = buildid

    def getDeviceJSONData(self):
        url = 'https://api.ipsw.me/v4/device/{}?type=ipsw'.format(self.device)
        r = urlopen(url).read().decode('utf-8')
        data = json.loads(r)
        return data

    def grab_signed_llb_iboot(self, path):
        signed = list()

        data = self.getDeviceJSONData()

        for i in range(0, len(data['firmwares'])):
            if data['firmwares'][i]['signed']:
                signed.append({
                    'version': data['firmwares'][i]['version'],
                    'buildid': data['firmwares'][i]['buildid'],
                    'url': data['firmwares'][i]['url']
                })

        for ii in range(0, len(signed)):
            url = signed[ii]['url']
            with RemoteZip(url) as f:
                stuff = Manifest(f.read('BuildManifest.plist'))
                paths = stuff.returnInfo()['paths']

                if not os.path.exists(path):
                    os.makedirs(path)

                for name in paths:
                    if 'LLB' in name:
                        out = '{}/{}'.format(
                            path,
                            os.path.basename(name['LLB']))
                        with f.open(name['LLB']) as copy, open(out, 'wb') as paste:
                            shutil.copyfileobj(copy, paste)

                    if 'iBoot' in name:
                        out = '{}/{}'.format(
                            path,
                            os.path.basename(name['iBoot']))
                        with f.open(name['iBoot']) as copy, open(out, 'wb') as paste:
                            shutil.copyfileobj(copy, paste)
