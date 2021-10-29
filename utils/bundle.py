import bsdiff4
import xdelta3
import io
import json
import os
import requests
import sys
import zipfile


class Bundle:
    def apply_patches(self, ipsw):
        with open(f'{self.bundle}/Info.json', 'r') as f:
            bundle_data = json.load(f)

        for patches in bundle_data['patches']:
            if patches != 'required':
                apply_patch = input(f"[NOTE] Would you like to apply '{patches}' patch to your custom IPSW? [Y\\N]: ").lower()
                if (apply_patch not in ('y', 'n')) or (apply_patch == 'n'):
                    continue

            for patch in bundle_data['patches'][patches]:
                if patch['patch'].split('.')[-1] == "delta":
                    with open(f"{ipsw}/{patch['file']}", "r+b") as ipsw_file, \
                         open(f"{self.bundle}/{patch['patch']}", "rb") as delta:
                        ipsw_file.write(xdelta3.decode(ipsw_file.read(), delta.read()))
                else:
                    bsdiff4.file_patch_inplace(f"{ipsw}/{patch['file']}", f"{self.bundle}/{patch['patch']}")

    def check_update_support(self):
        with open(f'{self.bundle}/Info.json', 'r') as f:
            bundle_data = json.load(f)

        return bundle_data['update_support']

    def fetch_bundle(self, device, version, buildid, path):
        bundle_name = f'{device}_{version}_{buildid}'
        bundle = requests.get(f'https://github.com/m1stadev/inferius-ext/raw/master/bundles/{bundle_name}.bundle')
        if bundle.status_code == 404:
            sys.exit(f'[ERROR] A Firmware Bundle does not exist for {device}, iOS {version}. Exiting.')

        output = f'{path}/{bundle_name}'
        with zipfile.ZipFile(io.BytesIO(bundle.content), 'r') as f:
            try:
                f.extractall(output)
            except OSError:
                sys.exit('[ERROR] Ran out of storage while extracting Firmware Bundle. Exiting.')

        self.bundle = output

    def verify_bundle(self, bundle, tmpdir, api, buildid, boardconfig):
        if not zipfile.is_zipfile(bundle):
            return False

        try:
            with zipfile.ZipFile(bundle, 'r') as f:
                try:
                    bundle_data = json.loads(f.read('Info.json'))
                except:
                    return False

            if not any(firm['buildid'] == buildid for firm in api['firmwares']):
                return False

            if not any(board.lower() == boardconfig.lower() for board in bundle_data['boards']):
                return False

        except:
            return False

        bundle_path = f"{tmpdir}/{bundle.split('/')[-1].rsplit('.', 1)[0]}"
        os.mkdir(bundle_path)
        with zipfile.ZipFile(bundle) as f:
            f.extractall(bundle_path)

        self.bundle = bundle_path
        return True
