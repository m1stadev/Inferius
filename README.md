# Inferius
Inferius is an [xpwn](https://github.com/OothecaPickle/xpwn)-like tool to create & restore custom IPSWs to 64-bit devices.

Its current purpose is to downgrade devices (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu)) to previous iOS versions. However, there are other possible uses for this tool as well.

## Notes and Caveats
Before using Inferius, keep in mind that
- **No one but YOU** is fully responsible for any data loss or damage caused to your device
- Creating a new IPSW when attempting to restore is a **must** when using Inferius. Previously created IPSWs can brick your device, depending on which LLB and iBoot files were used from a signed firmware
- Restores are **not** untethered. This means that in order to boot your device, you're always required to use [PyBoot](https://github.com/MatthewPierson/PyBoot) or [ra1nsn0w](https://github.com/tihmstar/ra1nsn0w) to do just that (or if you want to boot jailbroken, [checkra1n](https://checkra.in) will work fine too)
- Downgrades are still limited to versions compatible with the latest signed SEP version. This will change when [checkra1n](https://checkra.in/) implements a nonce setter for the SEP.

Inferius may not come with a firmware bundle compatible with your device. If you need to create your own firmware bundle, you can follow [this guide](https://github.com/marijuanARM/Inferius/wiki/Creating-your-own-Firmware-Bundles).

[Pull requests](https://github.com/marijuanARM/inferius-bundles/compare) for new firmware bundles are welcome, as long as the firmware bundle you want to add can create a usable IPSW for the targeted version.

## Usage
Currently, to use Inferius, you'll need
- A computer running macOS or Linux
- At least **10gbs** of free space on your computer
- An Internet Connection
- A 64-bit device (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu))
- A firmware bundle for your device & the iOS version to be downgraded to
- A brain (Not completely necessary, but YMMV)

## Requirements
- [libusb](https://libusb.info/)
- [My fork of futurerestore](https://github.com/marijuanARM/futurerestore)
- [My fork of img4tool](https://github.com/marijuanARM/img4tool)
- [libirecovery](https://github.com/libimobiledevice/libirecovery)
- [tsschecker](https://github.com/tihmstar/tsschecker)
- Pip dependencies:
    - `pip3 install -r requirements.txt`

To create a custom IPSW:
```py
./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW' -c [-v]
```

To create and restore a custom IPSW:
```py
./inferius.py -d 'device' -i 'iOS version' -f 'IPSW' -c -r [-v]
```

To restore a custom IPSW:
```py
./inferius.py -d 'device' -i 'iOS version' -f 'IPSW' -r [-v]
```

Below, you can find all the options Inferius has to offer

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-d DEVICE` | `--device DEVICE` | Device identifier (e.g. iPhone10,2) |
| `-i VERSION` | `--version VERSION` | iOS Version |
| `-f IPSW` | `--ipsw IPSW` | Path to IPSW |
| `-c` | `--create` | Create custom IPSW |
| `-r` | `--restore` | Restore custom IPSW |
| `-u` | `--update` | Keep data while restoring custom IPSW |

## To-Do
- Re-implement iOS 10 downgrades for A7 devices.
- Update bundle documentation
- Reimplement logs for debugging

## Special thanks
I'd like to thank the following individuals for their corresponding role in this project
- [NotHereForTheDong](https://github.com/NotHereForTheDong) for providing firmware bundles and beta testing
- [Renaitare](https://twitter.com/Renaitare), [Chibibowa](https://twitter.com/Chibibowa), and [Moses](https://twitter.com/MosesBuckwalter) for beta testing
- [Matty](https://twitter.com/mosk_i) for his special build of futurerestore, which allows custom IPSWs to be used for restoring

Finally, if you need help or have any questions about Inferius, join my [Discord server](https://discord.gg/fAngssA).
