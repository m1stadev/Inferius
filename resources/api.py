import requests

class API(object):
    def __init__(self, device_identifier, version):
        super().__init__()

        self.device = device_identifier

        self.v2_1_api = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed').json()
        self.check_device()
        self.boardconfig = self.fetch_boardconfig()

        self.v4_api = requests.get(f'https://api.ipsw.me/v4/device/{self.device}?type=ipsw').json()
    
    def check_device(self):
        if self.device not in self.v2_1_api['devices']:
            sys.exit(f'[ERROR] {self.device} does not exist. Exiting...')

    def check_version(self):
        if not any(firmwares[x]['version'] == self.version for x in range(len(self.v4_api['firmwares']))):
            sys.exit(f'[ERROR] {self.version} does not exist. Exiting...')

    def fetch_boardconfig(self):
        boardconfig = self.v4_api['boardconfig']

        if boardconfig == 'j171ap': # super jank fix for IPSW.me returning incorrect boardconfigs for the iPad7,11 and iPad7,12
            boardconfig = 'j172ap'

        elif boardconfig == 'j172ap':
            boardconfig = 'j171ap'

        return boardconfig
