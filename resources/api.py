import remotezip
import requests
import sys


class API(object):
	def __init__(self, identifier):
		self.check_device(identifier)
		self.api = self.fetch_api(identifier)
		self.boardconfig = self.fetch_boardconfig()

	def check_device(self, identifier):
		api = requests.get('https://api.ipsw.me/v4/devices').json()

		if identifier not in [x['identifier'] for x in api]:
			sys.exit(f"[ERROR] '{identifier}' does not exist. Exiting.")

	def check_signing(self, version):
		return any(firm['signed'] == True for firm in self.api['firmwares'] if firm['version'] == version)

	def check_version(self, version):
		if not any(firm['version'] == version for firm in self.api['firmwares']):
			sys.exit(f"[ERROR] '{version}' does not exist. Exiting.")

	def fetch_api(self, identifier):
		return requests.get(f'https://api.ipsw.me/v4/device/{identifier}?type=ipsw').json()

	def fetch_boardconfig(self):
		return [board['boardconfig'] for board in self.api['boards']]

	def fetch_latest(self, component, path):
		latest = self.api['firmwares'][0]
		with remotezip.RemoteZip(latest['url']) as ipsw:
			ipsw.extract(component, path)
		
		return latest['version']

	def fetch_sha1(self, buildid):
		return next(firm['sha1sum'] for firm in self.api['firmwares'] if firm['buildid'] == buildid)
