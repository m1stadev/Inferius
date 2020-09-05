#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from urllib.request import urlretrieve
from zipfile import ZipFile

from resources.api import API
from resources import ipsw, patch

host_os = platform.system()

# Taken and modified from https://github.com/Merculous/SHSHDump/blob/master/dump.py


def getldid():
    url = 'https://github.com/xerub/ldid/releases/download/42/ldid.zip'
    filename = os.path.basename(url)
    bin_path = 'resources/bin'
    zip_path = '{}/{}'.format(bin_path, filename)
    ldid_path = '{}/ldid'.format(bin_path)

    if not os.path.exists(ldid_path):
        print('Downloading ldid...')
        urlretrieve(url, zip_path)

        with ZipFile(zip_path, 'r') as f:
            if host_os == 'Darwin':
                print('Extracting MacOS ldid...')
                f.extract('ldid', bin_path)
                os.chmod(ldid_path, 0o755)

            elif host_os == 'Linux':
                with f.open('linux64/ldid') as yeet, open(ldid_path, 'wb') as yort:
                    print('Extracting Linux ldid...')
                    shutil.copyfileobj(yeet, yort)
                    os.chmod(ldid_path, 0o755)

    try:
        os.path.exists(ldid_path)
    except FileNotFoundError:
        print('Oof, we failed to download and extract ldid!')
        raise


def main():
    parser = ArgumentParser(
        description='Inferius - Create custom IPSWs for your 64bit iOS device!',
        usage="./inferius.py -i <PathToIPSW>")

    parser.add_argument(
        '-i',
        '--ipsw',
        help='Path to custom IPSW',
        nargs=1)

    args = parser.parse_args()

    # In case work directory is still here from a previous run, remove it
    if os.path.exists('work'):
        shutil.rmtree('work')

    ldid_check = subprocess.run(
        ('which',
         'ldid'),
        stdout=subprocess.PIPE,
        universal_newlines=True)

    # If we got a returncode of 1, then ldid is missing

    if ldid_check.returncode == 1:
        getldid()

    if args.ipsw:
        oof = API(args.ipsw[0])
        print(oof.grab_signed_llb_iboot('work/ipsw'))
    else:
        sys.exit(parser.print_help(sys.stderr))


if __name__ == '__main__':
    main()
