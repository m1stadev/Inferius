import glob
import os
import shutil
import subprocess
import sys
import time


class Restore(object):
	def __init__(self, identifier, platform):
		self.device = identifier
		self.platform = platform

	def restore(self, ipsw, cellular, update):
		args = [
			'futurerestore',
			'-t',
			self.blob,
			'--latest-sep',
		]

		if update:
			args.append('-u')

		if cellular:
			args.append('--latest-baseband')
		else:
			args.append('--no-baseband')

		args.append(ipsw)
		futurerestore = subprocess.run(args)
		if futurerestore.returncode != 0:
			sys.exit('[ERROR] Restore failed. Exiting.')

		shutil.rmtree(ipsw.rsplit('.', 0)[0])

	def save_blobs(self, boardconfig, ecid, apnonce, path):
		args = (
			'tsschecker',
			'-d',
			self.device,
			'-B',
			boardconfig,
			'-e',
			'0x' + ecid,
			'--apnonce',
			apnonce,
			'-l',
			'-s',
			'--save-path',
			path
			)

		tsschecker = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
		if 'Saved shsh blobs!' not in tsschecker.stdout:
			sys.exit('[ERROR] Failed to save blobs. Exiting.')

		self.blob = glob.glob(f'{path}/*.shsh*')[0]

		if self.platform != 8960:
			self.signing_blob = self.blob
			return

		args = (
			'tsschecker',
			'-d',
			self.device,
			'-B',
			boardconfig,
			'-e',
			'0x' + ecid,
			'-l',
			'-s',
			'--save-path',
			path
			)

		tsschecker = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
		if 'Saved shsh blobs!' not in tsschecker.stdout:
			sys.exit('[ERROR] Failed to save blobs. Exiting.')

		for blob in glob.glob(f'{path}/*.shsh*'):
			if blob != self.blob:
				self.signing_blob = blob
				break

	def send_component(self, file, component):
		if component == 'iBSS' and self.platform in (8960, 8015): #TODO: Reset device via pyusb rather than call an external binary.
			irecovery_reset = subprocess.run(('irecovery', '-f', file), stdout=subprocess.DEVNULL)
			if irecovery_reset.returncode != 0:
				sys.exit(f'[ERROR] Failed to reset connection. Exiting.')

		irecovery = subprocess.run(('irecovery', '-f', file), stdout=subprocess.DEVNULL)
		if irecovery.returncode != 0:
			sys.exit(f"[ERROR] Failed to send '{component}'. Exiting.")

		if component == 'iBEC':
			if 8010 <= self.platform <= 8015:
				irecovery_jump = subprocess.run(('irecovery', '-c', 'go'), stdout=subprocess.DEVNULL)
				if irecovery_jump.returncode != 0:
					sys.exit(f"[ERROR] Failed to boot '{component}'. Exiting.")

			time.sleep(2)

	def sign_component(self, file, output):
		args = (
			'img4tool',
			'-c',
			output,
			'-p',
			file,
			'-s',
			self.signing_blob
			)
			
		img4tool = subprocess.run(args, stdout=subprocess.DEVNULL)
		if img4tool.returncode != 0:
			sys.exit(f"[ERROR] Failed to sign '{file.split('/')[-1]}'. Exiting.")
