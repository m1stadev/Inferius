# Creating your own Firmware Bundles

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
            "kbag": {
                "key": "<IBSS_KEY>",
                "iv": "<IBSS_IV>"
            },
            "patch": "<IBSS_PATCH>"
        },
        "ibec": {
            "file": "<IBEC_PATH>",
            "sha1": "<IBEC_SHA1>",
            "kbag": {
                "key": "<IBEC_KEY>",
                "iv": "<IBEC_IV>"
            },
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

### `<*_KEY>`
- Replace `<*_KEY>` with the decryption key for the file. 
- This is only needed for the `ibss` and `ibec` entries.
- (e.g. The decryption key for the iOS 12.4 iBSS for the iPod7,1 is `fec516f5dbe916544339021ed4961cb60689c7c682d0f1dee6684179c995a0db`)

### `<*_IV>`
- Replace `<*_IV>` with the decryption IV for the file. 
- Like `<*_KEY>`, this is only needed for the `ibss` and `ibec` entries.
- (e.g. The decryption IV for the iOS 12.4 iBSS for the iPod7,1 is `3c5271964bf610e7ebccfc5822fac1f3`)

### `<*_PATCH>`
- Replace `<*_PATCH>` with a patch created by [bsdiff](https://github.com/mendsley/bsdiff) between the unpatched and patched components.

----

## Patches

### iBSS, iBEC
- Use [iBoot64Patcher](https://github.com/tihmstar/iBoot64Patcher), compiled with [Ralph0045's](https://twitter.com/Ralph0045) [liboffsetfinder64](https://github.com/Ralph0045/iBoot64Patcher) to patch iBSS and iBEC.
- Create a patch file using `bspatch <unpatched iBSS> <patched iBSS> <iBSS.patch>`, replacing `<unpatched iBSS>`, `<patched iBSS>`, and `<iBSS.patch>` with their respective names.

### Kernelcache
- Use [Ralph0045's](https://twitter.com/Ralph0045) [Kernel64Patcher](https://github.com/Ralph0045/Kernel64Patcher) to patch the kernel.
- Create a patch file using `bspatch <unpatched kernelcache> <patched kernelcache> <kernelcache.patch>`, replacing `<unpatched kernelcache>`, `<patched kernelcache>`, and `<kernelcache.patch>` with their respective names.

### ASR
- There is no tool to patch ASR automatically, so it must be done in a disassembler.
- Once you have patched ASR, create a patch file using `bspatch <unpatched ASR> <patched ASR> <ASR.patch>`, replacing `<unpatched ASR>`, `<patched ASR>`, and `<ASR.patch>` with their respective names.