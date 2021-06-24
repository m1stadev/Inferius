import remotezip
import requests
import sys


class API(object):
	def check_device(self, identifier):
		api = requests.get('https://api.ipsw.me/v4/devices').json()

		if identifier not in [device['identifier'] for device in api]:
			sys.exit(f"[ERROR] '{identifier}' does not exist. Exiting.")

		self.device = identifier

	def is_signed(self, version):
		return any(firm['signed'] == True for firm in self.api['firmwares'] if firm['version'] == version)

	def check_version(self, version):
		if not any(firm['version'] == version for firm in self.api['firmwares']):
			sys.exit(f"[ERROR] '{version}' does not exist. Exiting.")

	def fetch_api(self, identifier=None):
		self.api = requests.get(f'https://api.ipsw.me/v4/device/{identifier if identifier else self.device}?type=ipsw').json()

	def get_board(self):
		boards = [board['boardconfig'] for board in self.api['boards']]
		if len(boards) == 1:
			return boards[0]
		
		print('There are multiple boardconfigs for your device! Please choose the correct boardconfig for your device:')
		for board in range(len(boards)):
			print(f"  {board + 1}: {boards[board]}")

		board = input('Choice: ')
		try:
			board = int(board) - 1
		except:
			sys.exit('[ERROR] Invalid input given. Exiting.')
		else:
			if board not in range(len(boards)):
				sys.exit('[ERROR] Invalid input given. Exiting.')

		return boards[board]

	def partialzip_extract(self, buildid, component, path):
		firm = next(firm for firm in self.api['firmwares'] if firm['buildid'] == buildid)
		with remotezip.RemoteZip(firm['url']) as ipsw:
			ipsw.extract(component, path)

		return firm['version']

	def partialzip_read(self, buildid, component):
		firm = next(firm for firm in self.api['firmwares'] if firm['buildid'] == buildid)
		with remotezip.RemoteZip(firm['url']) as ipsw:
			return ipsw.read(component)

	def fetch_sha1(self, buildid):
		return next(firm['sha1sum'] for firm in self.api['firmwares'] if firm['buildid'] == buildid)
