import os
import glob
import subprocess
import sys
import usb

class Keys(object):
    def __init__(self, device_identifier, components, platform):
        super().__init__()

        self.device = device_identifier
        self.components = components
        self.platform = platform
        self.img4_check()

    def img4_check(self):
        img4_check = subprocess.run(('which', 'img4'), stdout=subprocess.PIPE, universal_newlines=True)
        if img4_check.returncode != 0:
            sys.exit("[ERROR] img4lib not installed! If img4lib is installed, make sure the 'img4' binary is in a directory on your PATH. Exiting...")

    def decrypt_keys(self):
        ibss_img4 = subprocess.run(('img4', '-i', f'.tmp/mass-decryptor/{self.components["ibss"]["file"]}', '-b'), stdout=subprocess.PIPE, universal_newlines=True)
        ibec_img4 = subprocess.run(('img4', '-i', f'.tmp/mass-decryptor/{self.components["ibec"]["file"]}', '-b'), stdout=subprocess.PIPE, universal_newlines=True)
        llb_img4 = subprocess.run(('img4', '-i', f'.tmp/mass-decryptor/{self.components["llb"]["file"]}', '-b'), stdout=subprocess.PIPE, universal_newlines=True)
        iboot_img4 = subprocess.run(('img4', '-i', f'.tmp/mass-decryptor/{self.components["iboot"]["file"]}', '-b'), stdout=subprocess.PIPE, universal_newlines=True)
        sep_img4 = subprocess.run(('img4', '-i', f'.tmp/mass-decryptor/{self.components["sep"]["file"]}', '-b'), stdout=subprocess.PIPE, universal_newlines=True)
            
        for x in (ibss_img4, ibec_img4, llb_img4, iboot_img4, sep_img4):
            if x.returncode != 0:
                sys.exit('[ERROR] Failed to get kbag from firmware image. Exiting...')
    
        keys = {}
        
        ibss_kbag = ibss_img4.stdout.split('\n')[0]
        ibec_kbag = ibec_img4.stdout.split('\n')[0]
        llb_kbag = llb_img4.stdout.split('\n')[0]
        iboot_kbag = iboot_img4.stdout.split('\n')[0]
        sep_kbag = sep_img4.stdout.split('\n')[0].lower()

        if not os.path.isdir('resources/ipwndfu'):
            if len(glob.glob('resources/ipwndfu*')) == 0:
                sys.exit("[ERROR] No ipwndfu detected in 'resources/'. Put a version of ipwndfu in 'resources/'. Exiting...")

            else:
                for x in glob.glob('resources/ipwndfu*'):
                    os.rename(x, 'resources/ipwndfu')
    
        os.chdir('resources/ipwndfu')

        ibss_decrypt = subprocess.run(f'./ipwndfu --decrypt-gid={ibss_kbag}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        ibec_decrypt = subprocess.run(f'./ipwndfu --decrypt-gid={ibec_kbag}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        llb_decrypt = subprocess.run(f'./ipwndfu --decrypt-gid={llb_kbag}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        iboot_decrypt = subprocess.run(f'./ipwndfu --decrypt-gid={iboot_kbag}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)

        for x in [ibss_decrypt, ibec_decrypt, llb_decrypt, iboot_decrypt]:
            if x.returncode != 0:
                sys.exit('[ERROR] Failed to decrypt kbag using the connected device. Exiting...')

        os.chdir('../../')

        keys['ibss'] = {"kbag": ibss_decrypt.stdout.split('\n')[1], "key": ibss_decrypt.stdout.split('\n')[1][-64:], "iv": ibss_decrypt.stdout.split('\n')[1][:32]}
        keys['ibec'] = {"kbag": ibec_decrypt.stdout.split('\n')[1], "key": ibec_decrypt.stdout.split('\n')[1][-64:], "iv": ibec_decrypt.stdout.split('\n')[1][:32]}
        keys['iboot'] = {"kbag": iboot_decrypt.stdout.split('\n')[1], "key": iboot_decrypt.stdout.split('\n')[1][-64:], "iv": iboot_decrypt.stdout.split('\n')[1][:32]}
        keys['llb'] = {"kbag": llb_decrypt.stdout.split('\n')[1], "key": llb_decrypt.stdout.split('\n')[1][-64:], "iv": llb_decrypt.stdout.split('\n')[1][:32]}
        keys['sep'] = {"kbag": sep_img4.stdout.split('\n')[0].lower(), "key": 'Unknown', "iv": 'Unknown'}

        self.keys = keys

        return keys

    def check_platform(self):
        try:
            device = usb.core.find(idVendor=0x5AC, idProduct=0x1227)

        except usb.core.NoBackendError:
            sys.exit('[ERROR] libusb is not installed. Install libusb from Homebrew. Exiting...')

        if device == None:
            sys.exit('[ERROR] Device in Pwned DFU mode not found. Exiting...')

        if device.serial_number.split(' ')[0].split(':')[1] != self.platform:
            sys.exit('[ERROR] Attempting to decrypt keys that cannot be decrypted with this device. Exiting...')

    def check_pwndfu(self):
        try:
            device = usb.core.find(idVendor=0x5AC, idProduct=0x1227)

        except usb.core.NoBackendError:
            sys.exit('[ERROR] libusb is not installed. Install libusb from Homebrew. Exiting...')

        if device == None:
            sys.exit('[ERROR] Device in Pwned DFU mode not found. Exiting...')

        if 'PWND:[checkm8]' not in device.serial_number:
            sys.exit('[ERROR] Attempting to decrypt keys with a device not in Pwned DFU mode. Exiting...')

    def save_keys(self, version, buildid):
        os.makedirs(f'keys/{self.device}/{version}/{buildid}', exist_ok=True)

        with open(f'keys/{self.device}/{version}/{buildid}/keys.txt', 'w') as f:
            f.write(f'Version: {version}\n')
            f.write(f'Device: {self.device}\n')
            f.write(f'Keys:\n')
            f.write('   iBSS:\n')
            f.write(f'      IV: {self.keys["ibss"]["iv"]}\n')
            f.write(f'      Key: {self.keys["ibss"]["key"]}\n')
            f.write(f'      KBAG: {self.keys["ibss"]["kbag"]}\n\n')
            f.write('   iBEC:\n')
            f.write(f'      IV: {self.keys["ibec"]["iv"]}\n')
            f.write(f'      Key: {self.keys["ibec"]["key"]}\n')
            f.write(f'      KBAG: {self.keys["ibec"]["kbag"]}\n\n')
            f.write('   LLB:\n')
            f.write(f'      IV: {self.keys["llb"]["iv"]}\n')
            f.write(f'      Key: {self.keys["llb"]["key"]}\n')
            f.write(f'      KBAG: {self.keys["llb"]["kbag"]}\n\n')
            f.write('   iBoot:\n')
            f.write(f'      IV: {self.keys["iboot"]["iv"]}\n')
            f.write(f'      Key: {self.keys["iboot"]["key"]}\n')
            f.write(f'      KBAG: {self.keys["iboot"]["kbag"]}')