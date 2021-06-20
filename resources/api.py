import remotezip
import requests
import sys

class API(object):
	def __init__(self, identifier):
		self.check_device(identifier)
		self.boardconfig = self.fetch_boardconfig()

	def check_device(self, device):
		api = requests.get(f'https://api.ipsw.me/v4/device/{device}type=ipsw')

		if api.status_code != 200:
			sys.exit(f"[ERROR] '{device}' does not exist. Exiting.")
		
		self.api = api.json()
		self.device = device

	def check_version(self, version):
		if not any(firm['version'] == version for firm in self.api['firmwares']):
			sys.exit(f"[ERROR] '{version}' does not exist. Exiting.")

	def check_signing(self, version):
		return any(firm['signed'] == True for firm in self.api['firmwares'] if firm['version'] == version)

	def fetch_boardconfig(self):
		return [board['boardconfig'] for board in self.api['boards']]

	def fetch_sha1(self, buildid):
		return next(firm['sha1sum'] for firm in self.api['firmwares'] if firm['buildid'] == buildid)

	def fetch_latest(self, component, path):
		latest = self.api['firmwares'][0]
		with remotezip.RemoteZip(latest['url']) as ipsw:
			ipsw.extract(component, path)
		
		return latest['version']
