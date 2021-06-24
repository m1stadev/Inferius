import bsdiff4
import io
import json
import os
import requests
import sys
import zipfile


class Bundle(object):
	def apply_patches(self, ipsw):
		with open(f'{self.bundle}/Info.json', 'r') as f:
			bundle_data = json.load(f)

		for patches in bundle_data['patches']:
			if patches != 'required':
				apply_patch = input(f"[NOTE] Would you like to apply '{patches}' patch to your custom IPSW? [Y\\N]: ").lower()
				if (apply_patch not in ('y', 'n')) or (apply_patch == 'n'):
					continue

			for patch in bundle_data['patches'][patches]:
				bsdiff4.file_patch_inplace('/'.join((ipsw, patch['file'])), '/'.join((self.bundle, patch['patch'])))

	def check_update_support(self):
		with open(f'{self.bundle}/Info.json', 'r') as f:
			bundle_data = json.load(f)

		return 'UpdateRamdisk' in bundle_data['patches']['required']

	def fetch_bundle(self, device, version, buildid, path):
		bundle_name = f'{device}_{version}_{buildid}_bundle'
		bundle = requests.get(f'https://github.com/m1stadev/inferius-ext/raw/master/bundles/{bundle_name}.zip')
		if bundle.status_code == 404:
			sys.exit(f'[ERROR] A Firmware Bundle does not exist for ({device}, {version}). Exiting.')

		output = '/'.join((path, bundle_name))
		with zipfile.ZipFile(io.BytesIO(bundle.content), 'r') as f:
			try:
				f.extractall(output)
			except OSError:
				sys.exit('[ERROR] Ran out of storage while extracting Firmware Bundle. Exiting.')

		self.bundle = output

	def verify_bundle(self, bundle, api, buildid, boardconfig):
		if not os.path.isfile('/'.join((bundle, 'Info.json'))):
			return False

		with open('/'.join((bundle, 'Info.json')), 'r') as f:
			try:
				bundle_data = json.load(f)
			except:
				return False

		try:
			if not any(firm['buildid'] == buildid for firm in api['firmwares']):
				return False

			if not any(board.lower() == boardconfig.lower() for board in bundle_data['boards']):
				return False

		except:
			return False


		self.bundle = bundle
		return True
