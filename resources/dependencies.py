import subprocess

class Checks(object):
    def __init__(self):
        super().__init__()

        self.check_futurerestore()
        self.check_tsschecker()
        self.check_irecovery()
        self.check_img4tool()


    def check_futurerestore(self):
        img4tool_commit = 'c0018d1260e5c41a989c13a2e8b956b85c164287'
        futurerestore_check = subprocess.run('which futurerestore', stdout=subprocess.DEVNULL, shell=True)

        if futurerestore_check.returncode != 0:
            sys.exit('[ERROR] FutureRestore is not installed on your system. Exiting...')

        custom_futurerestore_check = subprocess.run(('futurerestore'), stdout=subprocess.PIPE, universal_newlines=True)

        if custom_futurerestore_check.stdout.splitlines()[1].split('-')[-1] != img4tool_commit:
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