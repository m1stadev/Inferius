#!/usr/bin/env python3

from pathlib import Path
from pymobiledevice3.restore.device import Device
from pymobiledevice3.restore.ipsw.ipsw import IPSW
from pymobiledevice3.irecv import IRecv

from utils.api import API
from utils.bundle import Bundle

# from utils.device import Device
# from utils.ipsw import IPSW
from utils.manifest import Manifest, RestoreManifest
from utils.restore import Restore

import argparse
import platform
import sys
import tempfile


sys.tracebacklimit = 0


def create_ipsw(
    api: API, buildmanifest: Manifest, bundle: Bundle, ipsw: IPSW, tmpdir: Path
):
    print('Creating custom IPSW')

    print('[1] Grabbing Firmware Bundle...')
    if bundle.bundle is not None:
        print('Note: Using user provided Firmware Bundle.')
        try:
            bundle.verify_bundle(tmpdir, api.api, buildmanifest.buildid, api.board)
        except:
            sys.exit(f'[ERROR] Bundle is invalid: {bundle.bundle}. Exiting.')

    else:
        bundle.fetch_bundle(
            api.device, buildmanifest.version, buildmanifest.buildid, tmpdir
        )

    print('[2] Verifying IPSW...')
    ipsw.verify_ipsw(api.fetch_sha1(buildmanifest.buildid))

    print('[3] Extracting IPSW...')
    extracted_ipsw = tmpdir / 'ipsw'
    extracted_ipsw.mkdir()

    ipsw.extract_ipsw(extracted_ipsw)

    print('[4] Patching components...')
    bundle.apply_patches(extracted_ipsw)

    buildid = api.api['firmwares'][0]['buildid']
    latest_manifest = Manifest(
        api.partialzip_read(buildid, 'BuildManifest.plist'), api.board
    )

    api.partialzip_extract(buildid, latest_manifest.get_path('LLB'), extracted_ipsw)
    api.partialzip_extract(buildid, latest_manifest.get_path('iBoot'), extracted_ipsw)

    print('[5] Repacking IPSW...')
    ipsw.ipsw = ipsw.create_ipsw(
        extracted_ipsw,
        f'{ipsw.ipsw.stem}_custom.ipsw',
        bundle.check_update_support(),
        api.api['firmwares'][0]['version'],
    )
    print(f"Finished creating custom IPSW: '{ipsw.ipsw}'.\n")

    return ipsw


def restore_ipsw(
    api: API, buildmanifest: Manifest, ipsw: Path, updating: bool, tmpdir: Path
):
    print('Restoring custom IPSW')

    print('[1] Verifying custom IPSW...')
    # ipsw.verify_custom_ipsw(api, updating)

    print('[2] Checking for device in pwned DFU...')
    device = Device(irecv=IRecv())
    if 'PWND' not in device.irecv._device_info.keys():
        sys.exit(
            '[ERROR] Attempting to restore a device not in Pwned DFU mode. Exiting.'
        )

    sys.exit('im out!')

    print('[4] Saving SHSH blobs...')
    if buildmanifest.version[0] == 10:
        otamanifest = api.fetch_ota_manifest(api.device, tmpdir)
    else:
        otamanifest = None

    shsh_path = tmpdir / 'shsh'
    shsh_path.mkdir()
    if buildmanifest.version[0] == 10:
        restore.save_blobs(
            device.data['ECID'], device.board, shsh_path, manifest=otamanifest
        )
    else:
        restore.save_blobs(device.data['ECID'], device.board, shsh_path)

    print('[5] Signing bootchain...')
    rdsk_img = tmpdir / 'rdsk.dmg.img4'
    kern_img = tmpdir / 'rkrn.img4'
    restore.sign_image(ramdisk, rdsk_img)
    restore.sign_image(kernel, kern_img, tag='rkrn')

    print('[6] Restoring...')
    if buildmanifest.version[0] == 10:
        manifest = Manifest(api.partialzip_read('14G60', 'BuildManifest.plist'))
        sep = api.partialzip_extract('14G60', manifest.get_path('RestoreSEP'), tmpdir)
    else:
        sep = None

    restore.restore(
        ipsw.ipsw,
        rdsk_img,
        kern_img,
        device.baseband,
        updating,
        sep=sep,
        manifest=otamanifest,
    )

    print(
        f'Finished restoring custom IPSW to your device. Please boot your device using one of the tools listed in the README.\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Inferius - Create & Restore 64-bit custom IPSWs',
        usage="inferius -d 'identifier' -f 'IPSW' [-c/-r] [-b 'BUNDLE']",
    )
    parser.add_argument(
        '-d', '--device', help='Device identifier', nargs=1, required=True
    )
    parser.add_argument(
        '-f', '--ipsw', help='Path to IPSW', nargs=1, type=Path, required=True
    )
    parser.add_argument(
        '-c', '--create', help='Create custom IPSW', action='store_true'
    )
    parser.add_argument(
        '-r', '--restore', help='Restore custom IPSW', action='store_true'
    )
    parser.add_argument(
        '-b',
        '--bundle',
        help='(Optional) Path to local Firmware Bundle',
        nargs=1,
        type=Path,
    )
    parser.add_argument(
        '-u',
        '--update',
        help='(Optional) Keep data while restoring custom IPSW',
        action='store_true',
    )
    args = parser.parse_args()

    if (
        (not args.device or not args.ipsw)
        or (not args.create and not args.restore)
        or (args.update and not args.restore)
        or (args.bundle and not args.create)
    ):
        sys.exit(parser.print_help(sys.stderr))

    if platform.system() == 'Windows':
        sys.exit('[ERROR] Inferius does not support Windows. Exiting.')

    print('Inferius - Create & Restore 64-bit custom IPSWs\n')

    api = API(args.device[0])
    api.fetch_api()
    api.fetch_board()

    ipsw = IPSW(args.ipsw[0])
    restoremanifest = RestoreManifest(ipsw.read_file('Restore.plist'), api.board)
    if restoremanifest.platform not in (
        0x8960,
        0x7000,
        0x7001,
        0x8000,
        0x8001,
        0x8003,
        0x8010,
        0x8011,
        0x8015,
    ):
        sys.exit(f"[ERROR] '{api.device}' is not supported by Inferius. Exiting.")

    buildmanifest = Manifest(ipsw.read_file('BuildManifest.plist'), api.board)

    if not 10 <= buildmanifest.version[0] <= 14:
        sys.exit(
            f"[ERROR] iOS {'.'.join(str(_) for _ in buildmanifest.version)} is not supported by Inferius. Exiting."
        )

    if buildmanifest.version[0] == 10 and restoremanifest.platform != 0x8960:
        sys.exit(
            f'[ERROR] iOS 10 downgrades are only supported on A7 devices. Exiting.'
        )

    if args.device[0] not in buildmanifest.supported_devices:
        sys.exit(f"[ERROR] IPSW: {ipsw} does not support {api.device}. Exiting.")

    bundle = Bundle(args.bundle[0] if args.bundle else None)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        if args.create:
            custom_ipsw = create_ipsw(api, buildmanifest, bundle, ipsw, tmpdir)
        else:
            custom_ipsw = ipsw

        if args.restore:
            restore_ipsw(api, buildmanifest, args.ipsw[0], args.update, tmpdir)


if __name__ == '__main__':
    main()
