import os
import sys


class Bundle(object):
    def __init__(self, bundle):
        super().__init__()

        self.bundle = bundle

    def find_bundle(self, device, version):
        path = 'resources/FirmwareBundles/'
        bundle = '{}_{}_bundle'.format(device, version)

        if bundle not in os.listdir(path):
            sys.exit('{} does not exist in {}'.format(bundle, path))
