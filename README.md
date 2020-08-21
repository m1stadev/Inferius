# Inferius
Inferius is a tool to create custom IPSWs for 64-bit devices using Firmware Bundles, similarly to xpwn for 32-bit devices.

## Usage

```
usage: ./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW' [-v]

Inferius - Create and restore custom IPSWs to your 64bit iOS device!

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Your device identifier (e.g. iPhone10,2)
  -i VERSION, --version VERSION
                        The version of your stock IPSW
  -f IPSW, --ipsw IPSW  Stock IPSW to create into a custom IPSW
  -v, --verbose         Print verbose output for debugging
  ```

## Requirements
- A macOS system (Linux support may come in a future update).
- `ldid` from [Homebrew](https://brew.sh/).

## FAQ

### How do I create my own Firmware Bundles?
- There is a guide for creating your own Firmware Bundles in the [wiki](https://github.com/marijuanARM/Inferius/wiki/Creating-your-own-Firmware-Bundles).

### How can I contribute my own Firmware Bundles?
- Make a [Pull Request](https://github.com/marijuanARM/Inferius/compare)!
- Please make sure that the custom IPSW that your Firmware Bundle creates is usable before PRing.