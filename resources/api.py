import requests

class API(object):
    def __init__(self, device_identifier, version):
        super().__init__()

        self.device = device_identifier
        self.baseband = self.has_baseband()
        self.version = version
    
    def check_device(self):
        data = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed').json()

        if self.device not in data['devices']:
            sys.exit(f'[ERROR] {self.device} does not exist. Exiting...')

    def check_version(self):
        data = requests.get(f'https://api.ipsw.me/v4/device/{self.device}?type=ipsw').json()

        if not any(firmwares[x]['version'] == self.version for x in range(len(data['firmwares']))):
            sys.exit(f'[ERROR] {self.version} does not exist. Exiting...')