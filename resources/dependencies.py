import subprocess
import sys

class Checks(object):
	def __init__(self):
		super().__init__()

		self.check_futurerestore()
		self.check_tsschecker()
		self.check_irecovery()
		self.check_img4tool()

	def check_futurerestore(self):
		futurerestore_check = subprocess.run('which futurerestore', stdout=subprocess.DEVNULL, shell=True)
		if futurerestore_check.returncode != 0:
			sys.exit('[ERROR] FutureRestore is not installed on your system. Exiting...')

		futurerestore_version_check = subprocess.run(('futurerestore'), stdout=subprocess.PIPE, universal_newlines=True)
		if futurerestore_version_check.stdout.splitlines()[1][:-1].endswith('-m1sta'):
			sys.exit('[ERROR] This FutureRestore cannot be used with Inferius. Exiting...')

	def check_img4tool(self):
		img4tool_check = subprocess.run('which img4tool', stdout=subprocess.DEVNULL, shell=True)

		if img4tool_check.returncode != 0:
			sys.exit('[ERROR] img4tool is not installed on your system. Exiting...')

	def check_tsschecker(self):
		tsschecker_check = subprocess.run('which tsschecker', stdout=subprocess.DEVNULL, shell=True)

		if tsschecker_check.returncode != 0:
			sys.exit('[ERROR] tsschecker is not installed on your system. Exiting...')

	def check_irecovery(self):
		irecovery_check = subprocess.run('which irecovery', stdout=subprocess.DEVNULL, shell=True)

		if irecovery_check.returncode != 0:
			sys.exit('[ERROR] irecovery is not installed on your system. Exiting...')

		irecovery_version_check = subprocess.run(('irecovery', '-V'), stdout=subprocess.PIPE, universal_newlines=True)

		if 'unrecognized option' in irecovery_version_check.stdout:
			sys.exit('[ERROR] Your irecovery version is too old. Exiting...')