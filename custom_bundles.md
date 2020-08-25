# Creating your own Firmware Bundles
- Make sure to read through this whole page!

## Directory Structure
```
<Device_Identifier>_<iOS_Version>_bundle
├── 048-78047-092.asr.patch
├── Info.json
├── iBEC.n102.RELEASE.patch
├── iBSS.n102.RELEASE.patch
└── kernelcache.release.n102.patch
```
### `<Device_Identifier>`
- Replace `<Device_Identifier>` with the Device Identifier of the device the bundle is for (e.g. `iPhone10,2`).

### `<iOS_Version>`
- Should be self explanatory, replace `<iOS_Version>` with the iOS version that the bundle is for (e.g. `13.5`).

### Example
- `iPhone10,2_13.5_bundle`

----

## `Info.json`
```json
{
    "version": "<VERSION>",
    "boardconfig": "<BOARDCONFIG>",
    "processor": "<PROCESSOR>",
    "files": {
        "ibss": {
            "file": "<IBSS_PATH>",
            "sha1": "<IBSS_SHA1>",
            "patch": "<IBSS_PATCH>"
        },
        "ibec": {
            "file": "<IBEC_PATH>",
            "sha1": "<IBEC_SHA1>",
            "patch": "<IBEC_PATCH>"
        },
        "ramdisk": {
            "file": "<RAMDISK_PATH>",
            "sha1": "<RAMDISK_SHA1>",
            "patch": "<RAMDISK_PATCH>"
        },
        "kernelcache": {
            "file": "<KERNELCACHE_PATH>",
            "sha1": "<KERNELCACHE_SHA1>",
            "patch": "<KERNELCACHE_PATCH>"
        }
    }
}
```
### `<VERSION>`
- Replace `<VERSION>` with the iOS version that the bundle is for.
- (e.g. `13.5`)

### `<BOARDCONFIG>`
- Replace `<BOARDCONFIG>` with the shortened board config of the device the bundle is for.
- This can be found from the name of a component that contains the shortened board config in the IPSW.
- (e.g. you can get the board config `n102` from the file `Firmware/DFU/iBSS.n102.RELEASE.im4p`)

### `<PROCESSOR>`
- Replace `<VERSION>` with the processor that the device the bundle is for has.
- (e.g. iPhone 7 = `T8010`, iPhone 5S = `S5L8960`)

### `<*_PATH>`
- Replace `<*_PATH>` with the path to where the file is on the IPSW.
- (e.g. `<IBSS_PATH>` would be `Firmware/DFU/iBSS.*.RELEASE.im4p`)

### `<*_SHA1>`
- Replace `<*_SHA1>` with the sha1 hash of the unmodified file from the IPSW.
- (e.g. The sha1 hash of the iOS 12.4 iBSS for the iPod7,1 is `47c05552272bb413d280a24b63bb6b76b3301f87`)

### `<*_PATCH>`
- Replace `<*_PATCH>` with a patch created by [bsdiff](https://github.com/mendsley/bsdiff) between the unpatched and patched components.

----

## Patches

### iBSS, iBEC
- Using [img4tool](https://github.com/tihmstar/img4tool) or [img4lib](https://github.com/xerub/img4lib), decrypt and extract the iBSS from its im4p file:
    - img4tool: `img4tool -e --iv <IV> --key <KEY> -o ibss.raw <stock iBSS im4p>`.
    - img4lib: `img4 -i <stock iBSS im4p> -o ibss.raw -k <IV + KEY>`.
        - Replace `<stock iBSS im4p>` with the stock iBSS `.im4p` in your IPSW.
        - Replace `<IV>` with the IV to decrypt your iBSS, `<KEY>` with the key to decrypt your iBSS, and `<IV + KEY>` with the IV and key combined together.
- Use [iBoot64Patcher](https://github.com/tihmstar/iBoot64Patcher), compiled with [Ralph0045's](https://twitter.com/Ralph0045) [liboffsetfinder64](https://github.com/Ralph0045/iBoot64Patcher) to patch iBSS:
    - `iBoot64Patcher ibss.raw ibss.pwn`
- Repack the patched iBSS file into an im4p file with img4tool or img4lib:
    - img4tool: `img4tool -c patched_ibss.im4p -t ibss ibss.pwn`.
    - img4lib: `img4 -i ibss.pwn -o patched_ibss.im4p -A -T ibss`.
- Create a patch file with [bsdiff](https://github.com/mendsley/bsdiff):
    - `bsdiff <stock iBSS im4p> patched_ibss.im4p <iBSS.patch>`.
        - Replace `<stock iBSS im4p>` and `<iBSS.patch>` with their respective names.
- Repeat with iBEC.

### Kernelcache
- Use [img4tool](https://github.com/tihmstar/img4tool) or [img4lib](https://github.com/xerub/img4lib) to extract the kernelcache from its im4p file:
    - img4tool: `img4tool -e -o kernel.raw <stock kernelcache im4p>`.
    - img4lib: `img4 -i <stock kernelcache im4p> -o kernel.raw`.
        - Replace `<stock kernelcache im4p>` with the stock kernelcache `.im4p`.
- Use [Ralph0045's](https://twitter.com/Ralph0045) [Kernel64Patcher](https://github.com/Ralph0045/Kernel64Patcher) to patch the kernel:
    - `Kernel64Patcher kernel.raw kernel.patched -a`.
- Use [this](https://raw.githubusercontent.com/dualbootfun/dualbootfun.github.io/master/source/compareFiles.py) Python 3 script (credits: [mcg29](https://twitter.com/mcg29_)) to create a diff file between the unpatched and patched kernels:
    - `python3 compareFiles.py kernel.raw kernel.patched`.
- Use img4lib to apply the patch onto the stock kernelcache im4p:
    - `img4 -i <stock kernelcache image> -o kernelcache.release.*.patched -P kc.bpatch`.
- Create a patch file using [bsdiff](https://github.com/mendsley/bsdiff):
    - `bsdiff <stock kernelcache im4p> <patched kernelcache im4p> <kernelcache.patch>`
        - Replace `<stock kernelcache im4p>`, `<patched kernelcache im4p>`, and `<kernelcache.patch>` with their respective names.

### ASR
#### Extracting
- (Note: This currently requires a computer running macOS).
- Find the restore ramdisk in your IPSW. It is the smallest `.dmg` file.
- The restore ramdisk is inside of an im4p container. Extract the ramdisk from the im4p with [img4tool](https://github.com/tihmstar/img4tool) or [img4lib](https://github.com/xerub/img4lib):
    - img4tool: `img4tool -e -o stock_ramdisk.dmg <stock ramdisk dmg>`.
    - img4lib: `img4 -i <stock ramdisk dmg> -o stock_ramdisk.dmg`.
        - Replace `<stock ramdisk dmg>` with the restore ramdisk `.dmg` in your IPSW.
- Mount the ramdisk with `hdiutil`:
    - `hdiutil attach stock_ramdisk.dmg -mountpoint ramdisk`
- Copy the ASR binary to your working directory:
    - `cp ramdisk/usr/sbin/asr .`
- Unmount the ramdisk:
    - `hdiutil detach ramdisk`
#### Patching
- There is no tool to patch ASR automatically, so it must be done in a disassembler. Instructions to patch ASR will not be given here.
- After patching ASR, extract entitlements with `ldid` and resign the binary:
    - `ldid -e asr > entitlements.xml`
    - `ldid -Sentitlements.xml <patched ASR binary>`
        - Replace `<patched ASR binary>` with your patched ASR binary.
- Once you have patched ASR, extract a new ramdisk using img4tool or img4lib. This is what we will be using to create the patch between the stock and patched ramdisks:
    - img4tool: `img4tool -e -o patched_ramdisk.dmg <stock ramdisk dmg>`.
    - img4lib: `img4 -i <stock ramdisk dmg> -o patched_ramdisk.dmg`.
        - Replace `<stock ramdisk dmg>` with the restore ramdisk `.dmg` in your IPSW.
- Mount the ramdisk:
    - `hdiutil attach patched_ramdisk.dmg -mountpoint ramdisk`
- Copy the ASR binary into the ramdisk:
    - `cp <patched_asr> ramdisk/usr/sbin/asr`
        - If you get a `No space left on device` error, follow these steps:
            - Unmount the ramdisk:
                - `hdiutil detach ramdisk`
            - Find the size of the ramdisk in megabytes (If the size is a decimal number, round up to the nearest whole number).
            - Resize the ramdisk:
                - `hdiutil resize -size <SIZE>M patched_ramdisk.dmg`
                    - Replace `<SIZE>` with the size of your ramdisk in megabytes + 1
                        - Example: If the size of your ramdisk is 98 megabytes, run this command:
                            - `hdiutil resize -size 99M patched_ramdisk.dmg`
            - Mount the ramdisk again:
                - `hdiutil attach patched_ramdisk.dmg -mountpoint ramdisk`
            - Copy the ASR binary into the ramdisk, it should work now.
- Unmount the ramdisk:
    - `hdiutil detach ramdisk`
- Repack the patched ramdisk into an im4p container:
    - img4tool: `img4tool -c patched_ramdisk.im4p -t rdsk -d "0" patched_ramdisk.dmg`.
    - img4lib: `img4 -i patched_ramdisk.dmg -o patched_ramdisk.im4p -A -T rdsk -V "0"`.
        - Replace `<stock ramdisk dmg>` with the restore ramdisk `.dmg` in your IPSW.
- Create a patch file using [bsdiff](https://github.com/mendsley/bsdiff):
    - `bsdiff <stock ramdisk dmg> patched_ramdisk.dmg <ASR.patch>`.
        - Replace `<stock ramdisk dmg>` and `<ASR.patch>` with their respective names.
        - Note: This will take quite a while (took 10-20mins for me), so just give it time until it finishes!

## Note
- Due to the fact that A9 devices with the same device identifier can have different bootchain components, they must be created differently.
    - This does not apply to any other devices, including the A9X.
- For A9 devices, read the changes to the instructions below, and keep those in mind while creating your Firmware Bundle:

### `Info.json`

```json
{
    "version": "<VERSION>",
    "processor": "<PROCESSOR>",
    "devices": [
        {
            "boardconfig": "<BOARDCONFIG_1>",
            "files": {
                "ibss": {
                    "file": "<IBSS_PATH>",
                    "sha1": "<IBSS_SHA1>",
                    "patch": "<IBSS_PATCH>"
                },
                "ibec": {
                    "file": "<IBEC_PATH>",
                    "sha1": "<IBEC_SHA1>",
                    "patch": "<IBEC_PATCH>"
                }
            }
        },
        {
            "boardconfig": "<BOARDCONFIG_2>",
            "files": {
                "ibss": {
                    "file": "<IBSS_PATH>",
                    "sha1": "<IBSS_SHA1>",
                    "patch": "<IBSS_PATCH>"
                },
                "ibec": {
                    "file": "<IBEC_PATH>",
                    "sha1": "<IBEC_SHA1>",
                    "patch": "<IBEC_PATCH>"
                }
            }
        }
    ],
    "ramdisk": {
        "file": "<RAMDISK_PATH>",
        "sha1": "<RAMDISK_SHA1>",
        "patch": "<RAMDISK_PATCH>"
    },
    "kernelcache": {
        "file": "<KERNELCACHE_PATH>",
        "sha1": "<KERNELCACHE_SHA1>",
        "patch": "<KERNELCACHE_PATCH>"
    }
}
```
#### `<BOARDCONFIG_1>` and `<BOARDCONFIG_2>`
- With A9 devices, the `Info.json` is doubled, for each device with a seperate board config that shares a device identifier, but still have seperate bootchain components.
    - Example: `N71AP` and `N71mAP` both belong to the `iPhone8,1`, but they both have seperate iBSS files (`iBSS.n71.RELEASE.im4p` and `iBSS.n71m.RELEASE.im4p`) and iBEC files (`iBEC.n71.RELEASE.im4p` and `iBEC.n71m.RELEASE.im4p`).
        - In this example, `<BOARDCONFIG_1> = n71` and `<BOARDCONFIG_2> = n71m`. They do not need to be in any specific order, however

### Patches
- You will need to create patch files for the iBSS and iBEC of both devices.