# Inferius
Inferius is an [xpwn](https://github.com/planetbeing/xpwn)-like tool, written in Python, which can create custom IPSWs with firmware bundles & restore 64-bit devices using a custom IPSW.

Its current purpose is to downgrade devices (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu)) to previous iOS versions. However, there are other possible uses for this tool as well.

## Notes and Caveats
Before using Inferius, keep in mind that
- **No one but YOU** is fully responsible for any data loss or damage caused to your device
- Creating a new IPSW when attempting to restore is a **must** when using Inferius. Previously created IPSWs can brick your device, depending on which LLB and iBoot files were used from a signed firmware
- Restores are **not** untethered. This means that in order to boot your device, you're always required to use [PyBoot](https://github.com/MatthewPierson/PyBoot) or [ra1nsn0w](https://github.com/tihmstar/ra1nsn0w) to do just that (or if you want to boot jailbroken, [checkra1n](https://checkra.in) will work fine too)
- Downgrades are still limited to versions compatible with the latest signed SEP version. This will change when [checkra1n](https://checkra.in/) recieves a SEP bypass

Inferius may not come with a firmware bundle compatible with your device. If you need to create your own firmware bundle, you can follow [this guide](https://github.com/marijuanARM/Inferius/wiki/Creating-your-own-Firmware-Bundles).

[Pull requests](https://github.com/marijuanARM/Inferius/compare) for new firmware bundles are welcome, as long as the firmware bundle you want to add can create a usable IPSW for the targeted version.

## Usage
Currently, to use Inferius, you'll need
- A computer running macOS (Linux support may come in the future)
- At least **10gbs** of free space on your computer
- An Internet Connection
- A 64-bit device (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu))
- A firmware bundle for your device & the iOS version to be downgraded to
- A brain (Not completely necessary, but YMMV)

To create a custom IPSW with Inferius
```py
pip3 install -r requirements.txt
```
```py
./inferius.py -d 'device' -i 'iOS Version' -f 'IPSW' -c [-v]
```

To create a custom IPSW with Inferius and restore the custom IPSW onto your device
```py
./inferius.py -d 'device' -i 'iOS version' -f 'IPSW' -c -r [-v]
```

To restore a custom IPSW onto your device
```py
./inferius.py -d 'device' -i 'iOS version' -f 'IPSW' -r [-v]
```

Most options provided by both Inferius and Restituere are the same. Below, you can find all the options both tools have to offer

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-h` | `--help` | Shows all options avaiable |
| `-c` | `--create` | Create custom IPSW |
| `-d DEVICE` | `--device DEVICE` | Specifies your device indentifier (e.g iPhone 10,2) |
| `-i VERSION` | `--version VERSION` | Specifies the version of your stock/custom IPSW |
| `-f IPSW` | `--ipsw IPSW` | Specifies the path to the stock/custom IPSW |
| `-r` | `--restore` | Restore custom IPSW |
| `-u` | `--update` | Keeps your data when restoring (requires --restore) |
| `-v` | `--verbose` | Print verbose output for debugging |

## Special thanks
I'd like to thank the following individuals for their corresponding role in this project
- [NotHereForTheDong](https://github.com/NotHereForTheDong) for providing firmware bundles and beta testing
- [Renaitare](https://twitter.com/Renaitare), [Chibibowa](https://twitter.com/Chibibowa), and [Moses](https://twitter.com/MosesBuckwalter) for beta testing
- [Matty](https://twitter.com/mosk_i) for his special build of futurerestore, which allows custom IPSWs to be used for restoring

Finally, if you need help or have any questions about Inferius, join my [Discord server](https://discord.gg/fAngssA).
