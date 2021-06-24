# Inferius
Inferius is an [xpwn](https://github.com/m1stadev/xpwn)-like tool to create & restore custom IPSWs to 64-bit devices.

Its current purpose is to downgrade devices (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu)) to previous iOS versions. However, there are other possible uses for this tool as well.

## Notes and Caveats
Before using Inferius, keep in mind that
- **No one but YOU** is fully responsible for any data loss or damage caused to your device
- Downgrades are still limited to versions compatible with the latest signed SEP version. This will change when [checkra1n](https://checkra.in/) implements a nonce setter for the SEP.
- Due to the downgrades being tethered, after restoring a custom IPSW you must patch the bootchain & send it to your device over pwned DFU manually to boot, as described [here](https://dualbootfun.github.io/), or use one of these tools to automate the process for you:
    - [Ramiel](https://ramiel.app/)
    - [checkra1n](https://checkra.in)
    - [PyBoot](https://github.com/MatthewPierson/PyBoot)
    - [ra1nsn0w](https://github.com/tihmstar/ra1nsn0w)

By default, firmware bundles are automatically downloadeded from an [external repo](https://github.com/m1stadev/inferius-ext/tree/master/bundles). However, if there isn't a firmware bundle for the device+iOS version combo you're attempting to downgrade to, you'll need to create your own using [bundlegen](https://github.com/m1stadev/Inferius/blob/rewrite/bundlegen). More information on this script can be found below.

[Pull requests](https://github.com/m1stadev/inferius-ext/compare) for new firmware bundles are welcome, as long as the firmware bundle you want to add can create a usable IPSW for the targeted version.

## Usage
```py
./inferius -d 'Identifier' -f 'IPSW' [-c/-r] [-v]
```

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-d IDENTIFIER` | `--device IDENTIFIER` | Device identifier |
| `-f IPSW` | `--ipsw IPSW` | Path to IPSW |
| `-c` | `--create` | Create custom IPSW |
| `-r` | `--restore` | Restore custom IPSW |
| `-b` | `--bundle BUNDLE` | (Optional) Path to local Firmware Bundle |
| `-u` | `--update` | Keep data while restoring custom IPSW |

## To-Do
- Re-implement iOS 10 downgrades for A7 devices.
- Update bundle documentation

# Inferius Bundle Generator

## Usage
```py
./bundlegen -d 'Identifier' -i 'iOS Version'
```

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-d IDENTIFIER` | `--device IDENTIFIER` | Device identifier |
| `-i VERSION` | `--version VERSION` | iOS version |

## Requirements
- A computer running macOS
- At least **250mbs** of free space on your computer
- An Internet Connection
- A brain (Not completely necessary, but YMMV)
- [asr64_patcher](https://github.com/exploit3dguy/asr64_patcher)
    - Compiled binaries can be found [here](https://github.com/exploit3dguy/asr64_patcher/releases)
- [img4lib](https://github.com/xerub/img4lib)
    - Compiled binaries can be found [here](https://github.com/xerub/img4lib/releases)
- [kairos](https://github.com/dayt0n/kairos)
    - Compiled binaries can be found [here](https://github.com/dayt0n/kairos/releases)
- [Kernel64Patcher](https://github.com/Ralph0045/Kernel64Patcher)
- [Link Identity Editor](https://github.com/sbingner/ldid)
    - Compiled binaries can be found [here](https://github.com/sbingner/ldid/releases)
- Pip dependencies:
    - `pip3 install -r requirements.txt`

## Special thanks
I'd like to thank the following people for their corresponding role in this project
- [exploit3d](https://twitter.com/exploit3dguy) for his [asr64_patcher](https://github.com/exploit3dguy/asr64_patcher) tool
- [NotHereForTheDong](https://github.com/NotHereForTheDong) for creating many Firmware Bundles and beta testing
- [tale](https://twitter.com/aarnavtale), [Chibibowa](https://twitter.com/Chibibowa), and [Moses](https://twitter.com/MosesBuckwalter) for beta testing

Finally, if you need help or have any questions about Inferius, join my [Discord server](https://m1sta.xyz/discord).
