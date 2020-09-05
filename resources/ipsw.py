import hashlib
import json
import os
import shutil
import sys
from zipfile import ZipFile, is_zipfile


class IPSW(object):
    def __init__(self, ipsw):
        super().__init__()

        try:
            is_zipfile(ipsw)
        except IOError:
            print('{} is not a zip file!'.format(ipsw))
            raise
        else:
            with ZipFile(ipsw, 'r') as f:
                self.ipsw = f

    def verify_bootchain(self, firm_bundle, firm_bundle_number, verbose=False):
        with open('{}/Info.json'.format(firm_bundle)) as f:
            data = json.load(f)

            if firm_bundle_number == 1337:
                # FIXME
                bootchain_path = [data['files']['ibss']['file'], data['files']['ibec']['file'],
                                  data['files']['ramdisk']['file'], data['files']['kernelcache']['file']]

                bootchain_sha1 = [data['files']['ibss']['sha1'], data['files']['ibec']['sha1'],
                                  data['files']['ramdisk']['sha1'], data['files']['kernelcache']['sha1']]
            else:
                # FIXME
                bootchain_path = [data['devices'][firm_bundle_number]['files']['ibss']['file'], data['devices'][firm_bundle_number]
                                  ['files']['ibec']['file'], data['files']['ramdisk']['file'], data['files']['kernelcache']['file']]

                bootchain_sha1 = [data['devices'][firm_bundle_number]['files']['ibss']['sha1'], data['devices'][firm_bundle_number]
                                  ['files']['ibec']['sha1'], data['files']['ramdisk']['sha1'], data['files']['kernelcache']['sha1']]

        for x in range(0, len(bootchain_path)):
            with open('work/ipsw/{}'.format(bootchain_path[x]), 'rb') as f:
                # read contents of the file
                file_data = f.read()
                sha1_hash = str(hashlib.sha1(file_data).hexdigest())

            if sha1_hash == bootchain_sha1[x]:
                if verbose:
                    print('[VERBOSE] {} verified!'.format(bootchain_path[x]))

            else:
                sys.exit(
                    'work/ipsw/{} is not verified! Redownload your IPSW, and try again.\nExiting...'.format(bootchain_path[x]))

    def extract_ibss_ibec(self, ipsw, firm_bundle, firm_bundle_number, verbose=False):
        if os.path.isfile(ipsw):
            pass
        else:
            sys.exit('IPSW {} does not exist!\nExiting...'.format(ipsw))

        if is_zipfile(ipsw):
            if verbose:
                print('[VERBOSE] {} is a zip archive!'.format(ipsw))
        else:
            sys.exit('IPSW {} is not a valid IPSW!\nExiting...'.format(ipsw))

        with open('{}/Info.json'.format(firm_bundle)) as f:
            data = json.load(f)
            if firm_bundle_number == 1337:
                ibss_path = data['files']['ibss']['file']
                ibec_path = data['files']['ibec']['file']
            else:
                ibss_path = data['devices'][firm_bundle_number]['files']['ibss']['file']
                ibec_path = data['devices'][firm_bundle_number]['files']['ibec']['file']

        with ZipFile(ipsw, 'r') as ipsw:
            ipsw.extract(ibss_path, path='work/ipsw')

            if verbose:
                print(
                    '[VERBOSE] Extracted {} from IPSW to work/ipsw/'.format(ibss_path))

            ipsw.extract(ibec_path, path='work/ipsw')

            if verbose:
                print(
                    '[VERBOSE] Extracted {} from IPSW to work/ipsw/'.format(ibec_path))

            ipsw.close()

        return ibss_path, ibec_path

    def fetch_processor(self, firm_bundle):
        with open('{}/Info.json'.format(firm_bundle)) as f:
            data = json.load(f)
            return data['processor']

    def make_ipsw(self, ipsw_dir, firm_bundle, verbose=False):
        if os.path.isfile('{}_custom.ipsw'.format(firm_bundle[26:-7])):
            if verbose:
                print(
                    '[VERBOSE] Found custom IPSW from previous run: {}_custom.ipsw, deleting...'.format(firm_bundle[26:-7]))

            os.remove('{}_custom.ipsw'.format(firm_bundle[26:-7]))

        shutil.make_archive(firm_bundle[26:-7], 'zip', ipsw_dir)

        os.rename('{}.zip'.format(
            firm_bundle[26:-7]), '{}_custom.ipsw'.format(firm_bundle[26:-7]))

        return '{}_custom.ipsw'.format(firm_bundle[26:-7])
