import shutil
import subprocess
import sys


class Checks(object):
	def __init__(self):
		self.check_bin('futurerestore')
		self.check_bin('tsschecker')
		self.check_bin('irecovery')
		self.check_bin('img4tool')

	def check_bin(self, binary):
		if shutil.which(binary) is None:
			sys.exit(f"[ERROR] '{binary}' is not installed on your system. Exiting.")


		if binary == 'futurerestore':
			fr_ver = subprocess.run((binary), stdout=subprocess.PIPE, universal_newlines=True).stdout.splitlines()[0]
			if not fr_ver.endswith('-m1sta'):
				sys.exit(f"[ERROR] This '{binary}' cannot be used with Inferius. Exiting.")

		elif binary == 'irecovery':
			irec_ver = subprocess.run((binary, '-V'), stdout=subprocess.PIPE, universal_newlines=True).stdout

			if 'unrecognized option' in irec_ver.stdout:
				sys.exit(f"[ERROR] Your '{binary}' version is too old. Exiting.")
