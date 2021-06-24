import glob
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
			'--latest-sep'
		]

		if update:
			args.append('-u')

		if cellular:
			args.append('--latest-baseband')
		else:
			args.append('--no-baseband')

		args.append(ipsw)
		futurerestore = subprocess.run(args, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, universal_newlines=True)
		if 'Done: restoring succeeded!' not in futurerestore.stdout:
			sys.exit('[ERROR] Restore failed. Exiting.')

		shutil.rmtree(ipsw.rsplit('.', 1)[0])

	def save_blobs(self, ecid, boardconfig, path, apnonce=None):
		if apnonce:
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
				path,
				'--nocache'
				)

		else:
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
				path,
				'--nocache'
				)

		tsschecker = subprocess.check_output(args, universal_newlines=True)
		if 'Saved shsh blobs!' not in tsschecker:
			sys.exit('[ERROR] Failed to save blobs. Exiting.')

		if apnonce:
			for blob in glob.glob(f'{path}/*.shsh*'):
				if blob != self.signing_blob:
					self.blob = blob
					break
		else:
			self.signing_blob = glob.glob(f'{path}/*.shsh*')[0]

	def send_component(self, file, component):
		if component == 'iBSS' and self.platform in (8960, 8015): #TODO: Reset device via pyusb rather than call an external binary.
			irecovery_reset = subprocess.run(('irecovery', '-f', file), stdout=subprocess.DEVNULL)
			if irecovery_reset.returncode != 0:
				sys.exit('[ERROR] Failed to reset device. Exiting.')

		irecovery = subprocess.run(('irecovery', '-f', file), stdout=subprocess.DEVNULL)
		if irecovery.returncode != 0:
			sys.exit(f"[ERROR] Failed to send '{component}'. Exiting.")

		if component == 'iBEC':
			if 8010 <= self.platform <= 8015:
				irecovery_jump = subprocess.run(('irecovery', '-c', 'go'), stdout=subprocess.DEVNULL)
				if irecovery_jump.returncode != 0:
					sys.exit(f"[ERROR] Failed to boot '{component}'. Exiting.")

			time.sleep(3)

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
