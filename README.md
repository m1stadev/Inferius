# Criptam
Criptam is a tool written in Python to easily decrypt [Firmware Keys](https://www.theiphonewiki.com/wiki/Firmware_Keys) for iOS devices.

## Features
- Automatic uploading of decrypted keys to [TheiPhoneWiki](https://www.theiphonewiki.com/) (more on that below)
- Decrypt keys for *all* iOS versions for your iOS device
- Decrypt keys for other devices not including yours (requires the device you're decrypting for & the device you're decrypting with to share the same SoC)

## Requirements
- A macOS or Linux computer
- An Internet Connection
- A 64-bit device connected in pwned DFU mode (vulnerable to [checkm8](https://github.com/axi0mX/ipwndfu))
- A brain (Not completely necessary, but YMMV)
- Libraries:
    ```py
    pip3 install -r requirements.txt
    ```
- A version of ipwndfu at of `resources/ipwndfu` that supports your device
    - For A7, A10, and A11, use [this](https://github.com/axi0mX/ipwndfu) version
    - For A8 and A9, use [this](https://github.com/marijuanARM/ipwndfu-t7000-s8000-s8003) version


## Usage
| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-h` | `--help` | Shows all options avaiable |
| `-d DEVICE` | `--device DEVICE` | Device identifier (ex. iPhone9,3) |
| `-v VERSION` | `--version VERSION` | Decrypt keys for a single iOS version |
| `-w` | `--wiki` | Save decrypted keys in TheiPhoneWiki format |
| `-u` | `--upload` | Upload decrypted keys to TheiPhoneWiki |
| `-s` | `--save` | Save decrypted keys in txt format |

## Wiki Uploading
- Uploading keys to [TheiPhoneWiki](https://www.theiphonewiki.com/) requires you to have an account.
- If there are already keys for the version you are trying to decrypt, Criptam will not overwrite them.
- Criptam will ask for your wiki login information before uploading if you choose to upload. This is **not** saved anywhere.