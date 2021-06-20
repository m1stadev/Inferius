import bsdiff4
import json
import os
import requests
import sys
import zipfile

class Bundle(object):
	def __init__(self, ipsw_path):
		self.ipsw = ipsw_path

	def fetch_bundle(self, device, version, buildid):
		bundle = requests.get(f'https://github.com/m1stadev/inferius-ext/raw/master/{device}_{version}_{buildid}_bundle.zip')
		if bundle.status_code == 404:
			sys.exit(f'[ERROR] A Firmware Bundle does not exist for device: {device}, version: {version}. Exiting.')

		#os.makedirs(f'.tmp/Inferius/{device}_{version}_bundle')

		with open(f'.tmp/Inferius/{device}_{version}_{buildid}_bundle.zip', 'wb') as f:
			f.write(bundle.content)

		with zipfile.ZipFile(f'.tmp/Inferius/{device}_{version}_{buildid}_bundle.zip', 'r') as f:
			try:
				f.extractall(f'.tmp/Inferius/{device}_{version}_{buildid}_bundle')
			except OSError:
				sys.exit('[ERROR] Ran out of storage while extracting Firmware Bundle. Ensure you have at least 10gbs of free space on your computer, then try again. Exiting.', is_verbose)

		os.remove(f'.tmp/Inferius/{device}_{version}_{buildid}_bundle.zip')

		self.bundle = f'.tmp/Inferius/{device}_{version}_{buildid}_bundle'

	def check_update_support(self):
		with open(f'{self.bundle}/Info.json', 'r') as f:
			bundle_data = json.load(f)

		if 'UpdateRamdisk' in bundle_data['patches']['required']:
			return True

		return False

	def apply_patches(self):
		patched_components = list()

		with open(f'{self.bundle}/Info.json', 'r') as f:
			bundle_data = json.load(f)

		for x in bundle_data['patches']:
			if x == 'required':
				continue

			apply_patch = input(f"[NOTE] Would you like to apply '{x}' patch to your custom IPSW? [Y\\N]: ").lower()

			if apply_patch not in ('y', 'n'):
				print(f"[ERROR] Invalid input given, not applying '{x}' patch.")
				continue

			if apply_patch == 'n':
				print(f"[ERROR] Requested not to apply '{x}' patch.")
				continue

			for i in bundle_data['patches'][x]:
				patched_components.append(i)
				bsdiff4.file_patch_inplace(f"{self.ipsw}/{bundle_data['patches'][x][i]['file']}", f"{self.bundle}/{bundle_data['patches'][x][i]['patch']}")

		for x in bundle_data['patches']['required']:
			if x in patched_components:
				continue

			bsdiff4.file_patch_inplace(f"{self.ipsw}/{bundle_data['patches']['required'][x]['file']}", f"{self.bundle}/{bundle_data['patches']['required'][x]['patch']}")