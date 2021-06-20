import remotezip
import requests
import sys

class API(object):
	def __init__(self, device_identifier):
		super().__init__()

		self.device = device_identifier

		self.api = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed').json()
		self.check_device()
		self.boardconfig = self.fetch_boardconfig()

	def check_device(self):
		if self.device not in self.api['devices']:
			sys.exit(f'[ERROR] {self.device} does not exist. Exiting.')

	def check_version(self, version):
		if not any(self.api['devices'][self.device]['firmwares'][x]['version'] == version for x in range(len(self.api['devices'][self.device]['firmwares']))):
			sys.exit(f'[ERROR] {version} does not exist. Exiting.')

	def check_signing(self, version):
		if any(self.api['devices'][self.device]['firmwares'][x]['signed'] == True for x in range(len(self.api['devices'][self.device]['firmwares'])) if self.api['devices'][self.device]['firmwares'][x]['version'] == version):
			return True

		return False

	def fetch_boardconfig(self):
		device_boardconfigs = list()
		all_boardconfigs = requests.get('https://gist.githubusercontent.com/m1stadev/6041aa45974c047b3d75da98b9926210/raw/95993516bdd086cf4b23d2771d57d0ef75bc6540/boardconfigs.json').json()
		for x in all_boardconfigs[self.device]:
			device_boardconfigs.append(x.lower())

		return device_boardconfigs

	def fetch_sha1(self, buildid): return next(self.api['devices'][self.device]['firmwares'][x]['sha1sum'] for x in range(len(self.api['devices'][self.device]['firmwares'])) if self.api['devices'][self.device]['firmwares'][x]['buildid'] == buildid)

	def fetch_latest(self, component, path):
		with remotezip.RemoteZip(self.api['devices'][self.device]['firmwares'][0]['url']) as ipsw:
			ipsw.extract(component, path)
		
		return self.api['devices'][self.device]['firmwares'][0]['version']
