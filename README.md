# Inferius
Inferius (alongside Restituere) is an [xpwn](https://github.com/planetbeing/xpwn)-like tool, written in Python, which can create custom IPSWs with firmware bundles & restore 64-bit devices using a custom IPSW.

Its current purpose is to downgrade devices (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu)) to previous iOS versions. However, the tool can (theoretically) be used by other applications.

## Notes and Caveats
Before using Inferius, keep in mind that
- **No one but YOU** is fully responsible for any data loss or damage caused to your device
- Creating new IPSW when attempting to restore is a good practice when using Inferius. Previously created IPSWs can brick your device, depending on which LLB and iBoot files were used from a signed firmware
- Restores are **not** untethered. This means that in order to boot your device, you're always required to use [PyBoot](https://github.com/MatthewPierson/PyBoot) or [ra1nsn0w](https://github.com/tihmstar/ra1nsn0w) to do just that
- Downgrades are still limited to versions compatible with your current installed SEP version. This will change when [checkra1n](https://checkra.in/) recieves an SEP bypass

Inferius may not come with a firmware bundle compatible with your device. If you need to create your own firmware bundle, you can follow [this guide](https://github.com/marijuanARM/Inferius/wiki/Creating-your-own-Firmware-Bundles).

[Pull requests](https://github.com/marijuanARM/Inferius/compare) for new firmware bundles are welcome, as long as the firmware bundle you want to add can create a usable IPSW for the targeted version.

## Usage
Currently, to use Inferius, you'll need
- A computer running macOS (Linux support may come in the future)
- A 64-bit device (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu))
- A firmware bundle for the device you are wanting to restore and the version you are wanting to downgrade to
- `ldid` (You can install it from [Homebrew](https://brew.sh/))
- A brain (Not completely necessary, but YMMV)

To create a custom IPSW with Inferius
```py
./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW' [-v]
```

To restore your device with the created IPSW with Restituere
```py
./restituere.py -d 'device' -i 'iOS version' -f 'IPSW' [-v]
```

Most options provided by both Inferius and Restituere are the same. Below, you can find all the options both tools have to offer

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-h` | `--help` | Shows all options avaiable |
| `-d DEVICE` | `--device DEVICE` | Specifies your device indentifier (e.g iPhone 10,2) |
| `-i VERSION` | `--version VERSION` | Specifies the version of your stock/custom IPSW |
| `-f IPSW` | `--ipsw IPSW` | Specifies the path to the stock/custom IPSW |
| `-v` | `--verbose` | Print verbose output for debugging |
| `-u` | `--update` | Keeps your data when restoring (Experimental, only for Restituere)

## Special thanks
I'd like to thank the following individuals for their corresponding role in this project
- [NotHereForTheDong](https://github.com/NotHereForTheDong) for providing firmware bundles and beta testing
- [Renaitare](https://twitter.com/Renaitare), [Chibibowa](https://twitter.com/Chibibowa), and [Moses](https://twitter.com/MosesBuckwalter) for beta testing
- [Matty](https://twitter.com/mosk_i) for his special build of futurerestore, which allows custom IPSWs to be used for restoring

Finally, if you need help or have any questions about Inferius, join my [Discord server](https://discord.gg/fAngssA).
