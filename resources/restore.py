import glob
import os
import shutil
import subprocess
import sys
import time

class Restore(object):
	def __init__(self, device_identifier, platform):
		super().__init__()

		self.device = device_identifier
		self.platform = platform

	def save_blobs(self, boardconfig, ecid, apnonce, update, path):
		args= [
			'tsschecker',
			'-d',
			self.device,
			'-l',
			'-e',
			f'0x{ecid}',
			'-s',
			'-B',
			boardconfig,
			'--apnonce',
			apnonce,
			'--save-path',
			path
		]

		if update:
			args.insert(5, '-u')

		tsschecker = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)

		if tsschecker.returncode != 0:
			sys.exit('[ERROR] Failed to save blobs. Exiting.')

		for f in glob.glob(f'{path}/*.shsh*'):
			self.blob = f
			break

		if self.platform == 8960:
			args= [
				'tsschecker',
				'-d',
				self.device,
				'-l',
				'-e',
				f'0x{ecid}',
				'-s',
				'-B',
				boardconfig,
				'--save-path',
				path
			]

			if update:
				args.insert(5, '-u')

			tsschecker = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)

			for f in glob.glob(f'{path}/*.shsh*'):
				if f != self.blob:
					self.signing_blob = f
					break

		else:
			self.signing_blob = self.blob

	def sign_component(self, file, output):
		img4tool = subprocess.run(('img4tool', '-c', f'{output}/{file.split("/")[-1].rsplit(".", 1)[0]}.img4', '-p', file, '-s', self.signing_blob), stdout=subprocess.PIPE, universal_newlines=True)

		if img4tool.returncode != 0:
			sys.exit(f"[ERROR] Failed to sign '{file.split('/')[-1]}'. Exiting.")

	def send_component(self, file, component):
		if component == 'iBSS' and self.platform in (8960, 8015):
			irecovery_reset = subprocess.run(('irecovery', '-f', file), stdout=subprocess.PIPE, universal_newlines=True)

			if irecovery_reset.returncode != 0:
				sys.exit(f'[ERROR] Failed to reset connection. Exiting.')

		irecovery = subprocess.run(('irecovery', '-f', file), stdout=subprocess.PIPE, universal_newlines=True)
		if irecovery.returncode != 0:
			sys.exit(f'[ERROR] Failed to send {component}. Exiting.')

		if component == 'iBEC' and 8010 <= self.platform <= 8015:
			irecovery_jump = subprocess.run(('irecovery', '-c', 'go'), stdout=subprocess.PIPE, universal_newlines=True)

			if irecovery_jump.returncode != 0:
				sys.exit(f'[ERROR] Failed to boot {component}. Exiting.')

			time.sleep(2)
		elif component == 'iBEC':
			time.sleep(2)

	def restore(self, ipsw, cellular, update):
		args = [
			'futurerestore',
			'-t',
			self.blob,
			'--latest-sep',
			ipsw
		]

		if update:
			args.insert(3, '-u')

		if cellular:
			args.insert(4, '--latest-baseband')
		else:
			args.insert(4, '--no-baseband')

		futurerestore = subprocess.run(args)

		if futurerestore.returncode != 0:
			sys.exit('[ERROR] Restore failed. Exiting.')

		shutil.rmtree(f'IPSWs/{ipsw.rsplit(".", 1)[0]}')