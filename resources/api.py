import remotezip
import requests

class API(object):
    def __init__(self, device_identifier, version):
        super().__init__()

        self.device = device_identifier

        self.v2_1_api = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed').json()
        self.check_device()
        self.boardconfig = self.fetch_boardconfig()

        self.v4_api = requests.get(f'https://api.ipsw.me/v4/device/{self.device}?type=ipsw').json()

        self.version = version

    def check_device(self):
        if self.device not in self.v2_1_api['devices']:
            sys.exit(f'[ERROR] {self.device} does not exist. Exiting...')

    def check_version(self):
        if not any(self.v4_api['firmwares'][x]['version'] == self.version for x in range(len(self.v4_api['firmwares']))):
            sys.exit(f'[ERROR] {self.version} does not exist. Exiting...')

    def fetch_boardconfig(self):
        boardconfig_list = requests.get('https://gist.githubusercontent.com/marijuanARM/6041aa45974c047b3d75da98b9926210/raw/95993516bdd086cf4b23d2771d57d0ef75bc6540/boardconfigs.json').json()
        boardconfigs = []
        for x in boardconfig_list[self.device]:
            boardconfigs.append(x.lower())

        return boardconfigs

    def fetch_sha1(self, buildid): return next(self.v4_api['firmwares'][x]['sha1sum'] for x in range(len(self.v4_api['firmwares'])) if self.v4_api['firmwares'][x]['buildid'] == buildid)

    def fetch_latest(self, component, path):
        with remotezip.RemoteZip(self.v4_api['firmwares'][0]['url']) as ipsw:
            ipsw.extract(component, path)