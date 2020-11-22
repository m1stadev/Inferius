#!/usr/bin/env python3

from resources import device, ipsw, keys, manifest, wiki
import atexit
import argparse
import getpass
import glob
import os
import platform
import requests
import shutil
import sys

if platform.system() == 'Windows':
    sys.exit('[ERROR] Windows systems are not supported. Exiting...')

def cleanup():
    if os.path.isdir('.tmp'):
        shutil.rmtree('.tmp')

def device_check(device):
    api = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed')
    data = api.json()
    if device in data['devices']:
        return True

atexit.register(cleanup)

def main():
    parser = argparse.ArgumentParser(description='Key Fetcher', usage="./key-fetcher.py -d 'device' [-i 'version']")
    parser.add_argument('-d', '--device', help='Device identifier (ex. iPhone9,3)', nargs=1)
    parser.add_argument('-w', '--wiki', help='Save decrypted keys in TheiPhoneWiki format', action='store_true')
    parser.add_argument('-u', '--upload', help='Upload decrypted keys to TheiPhoneWiki', action='store_true')
    parser.add_argument('-s', '--save', help='Save decrypted keys in txt format', action='store_true')
    parser.add_argument('-v', '--version', help='Decrypt keys for a single iOS version', nargs=1)
    args = parser.parse_args()

    if not args.device:
        sys.exit(parser.print_help(sys.stderr))

    if not device_check(args.device[0]):
        sys.exit(f'[ERROR] Device {args.device[0]} does not exist. Exiting...')

    cleanup()

    os.makedirs('.tmp/mass-decryptor')

    if args.upload:
        wiki_user = input('TheiPhoneWiki username: ')
        wiki_pass = getpass.getpass('TheiPhoneWiki password: ')

    api = requests.get(f'https://api.ipsw.me/v4/device/{args.device[0]}?type=ipsw')
    data = api.json()
    device_identifier = data['identifier']
    boardconfig = data['boardconfig']

    valid_device = None

    for v in range(0, len(data['firmwares'])):
        version = data['firmwares'][v]['version']
        buildid = data['firmwares'][v]['buildid']

        if args.version and version != args.version[0]:
            continue

        if version.startswith('7') or version.startswith('8') or version.startswith('9'):
            sys.exit('[ERROR] Decrypting pre-iOS 10 version are not supported yet. Exiting...')

        template = device.Device(args.device[0], version)
        wiki_template = template.template

        ipsw_download = data['firmwares'][v]['url'].replace('http://updates-http', 'https://updates')
        
        ipsw_dl = ipsw.IPSW(device_identifier, version, ipsw_download)
        bm = ipsw_dl.manifest
        rm = ipsw_dl.restoremanifest

        if bm == False:
            continue

        with open(bm, 'rb') as f:
            buildmanifest = manifest.Manifest(f, boardconfig, template.required_components)

        with open(rm, 'rb') as f:
            restoremanifest = manifest.RestoreManifest(f, device_identifier, data['boardconfig'])

        ipsw_dl.download_components(buildmanifest.components)

        decrypt = keys.Keys(device_identifier, buildmanifest.components, restoremanifest.fetch_platform())
        if valid_device == None:
            decrypt.check_pwndfu()
            decrypt.check_platform()
            valid_device = True

        decrypt.decrypt_keys()

        for x in glob.glob('.tmp/mass-decryptor/*'):
            os.remove(x)

        wiki_upload = wiki.Wiki(device_identifier, buildid, version, buildmanifest.codename, buildmanifest.components)
        wiki_page = wiki_upload.make_keypage(decrypt.keys, wiki_template, ipsw_download)

        if args.wiki:
            wiki_upload.save_keys(wiki_page)
            print(f"iOS {version}'s keys for {device_identifier} in TheiPhoneWiki format written to 'keys/{device_identifier}/{version}/{buildid}/wiki_keys.txt'")

        if args.upload:
            wiki_upload.login_info(wiki_user, wiki_pass)
            wiki_upload.upload_to_wiki(wiki_page)

        if args.save:
            decrypt.save_keys(version, buildid)

            print(f"iOS {version}'s keys for {device_identifier} written to 'keys/{device_identifier}/{version}/{buildid}/keys.txt'")
        elif not args.wiki and not args.upload:
            print(f"iOS {version}'s keys for {device_identifier}:\niBSS KBAG: {decrypt.keys['ibss']['kbag']}\niBEC KBAG: {decrypt.keys['ibec']['kbag']}\niBoot KBAG: {decrypt.keys['iboot']['kbag']}\nLLB KBAG: {decrypt.keys['llb']['kbag']}")

        if args.version:
            break

    print('Done!')

    shutil.rmtree('.tmp')

if __name__ == '__main__':
    main()