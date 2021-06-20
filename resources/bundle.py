import bsdiff4
import json
import os
import requests
import sys
import zipfile

class Bundle(object):
	def __init__(self, ipsw_path):
		self.ipsw = ipsw_path

	def fetch_bundle(self, device, version, buildid, tmpdir):
		bundle_name = f'{device}_{version}_{buildid}_bundle'
		bundle = requests.get(f'https://github.com/m1stadev/inferius-ext/raw/master/bundles/{bundle_name}.zip')
		if bundle.status_code == 404:
			sys.exit(f'[ERROR] A Firmware Bundle does not exist for ({device}, {version}). Exiting.')

		with zipfile.ZipFile(bundle.content, 'r') as f:
			try:
				f.extractall(f'{tmpdir}/bundle_name')
			except OSError:
				sys.exit('[ERROR] Ran out of storage while extracting Firmware Bundle. Exiting.')

		self.bundle = '/'.join((tmpdir, bundle_name))

	def check_update_support(self):
		with open(f'{self.bundle}/Info.json', 'r') as f:
			bundle_data = json.load(f)

		return 'UpdateRamdisk' in bundle_data['patches']['required']

	def apply_patches(self):
		with open(f'{self.bundle}/Info.json', 'r') as f:
			bundle_data = json.load(f)

		for patches in bundle_data['patches']:
			if patches != 'required':
				apply_patch = input(f"[NOTE] Would you like to apply '{patches}' patch to your custom IPSW? [Y\\N]: ").lower()
				if (apply_patch not in ('y', 'n')) or (apply_patch == 'n'):
					continue

			for patch in bundle_data['patches'][patches]:
				bsdiff4.file_patch_inplace(f"{self.ipsw}/{patch['file']}", f"{self.bundle}/{patch['patch']}")
