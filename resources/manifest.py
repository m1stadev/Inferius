import plistlib

class Manifest(object):
    def __init__(self, manifest, boardconfig, required_components):
        super().__init__()

        self.manifest = plistlib.load(manifest)
        self.required_components = required_components
        self.boardconfig = boardconfig
        self.codename = self.manifest['BuildIdentities'][0]['Info']['BuildTrain']
        self.components = self.fetch_components()

    def fetch_components(self):
        components = {}

        for i in range(0, len(self.manifest['BuildIdentities'])):
            if not self.manifest['BuildIdentities'][i]['Info']['DeviceClass'] == self.boardconfig:
                continue

            if self.manifest['BuildIdentities'][i]['Info']['RestoreBehavior'] == 'Update':
                components['updateramdisk'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['RestoreRamDisk']['Info']['Path'], "encrypted": False}
            
            if self.manifest['BuildIdentities'][i]['Info']['RestoreBehavior'] == 'Erase':
                components['restoreramdisk'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['RestoreRamDisk']['Info']['Path'], "encrypted": False}

            components['rootfs'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['OS']['Info']['Path'], "encrypted": False}
            components['applelogo'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['AppleLogo']['Info']['Path'], "encrypted": False}
            components['batterycharging0'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BatteryCharging0']['Info']['Path'], "encrypted": False}
            components['batterycharging1'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BatteryCharging1']['Info']['Path'], "encrypted": False}
            components['batteryfull'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BatteryFull']['Info']['Path'], "encrypted": False}
            components['batterylow0'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BatteryLow0']['Info']['Path'], "encrypted": False}
            components['batterylow1'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BatteryLow1']['Info']['Path'], "encrypted": False}
            components['glyphplugin'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BatteryPlugin']['Info']['Path'], "encrypted": False}
            components['devicetree'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['DeviceTree']['Info']['Path'], "encrypted": False}
            components['kernelcache'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['KernelCache']['Info']['Path'], "encrypted": False}
            components['llb'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['LLB']['Info']['Path'], "encrypted": True}
            components['recoverymode'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['RecoveryMode']['Info']['Path'], "encrypted": False}
            components['sep'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['SEP']['Info']['Path'], "encrypted": True}
            components['ibec'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['iBEC']['Info']['Path'], "encrypted": True}
            components['ibss'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['iBSS']['Info']['Path'], "encrypted": True}
            components['iboot'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['iBoot']['Info']['Path'], "encrypted": True}

            if self.required_components['baseband']:
                components['baseband'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['BasebandFirmware']['Info']['Path'], "version": self.manifest['BuildIdentities'][i]['Manifest']['BasebandFirmware']['Info']['Path'].split('-')[1][:-13], "encrypted": False}

            if self.required_components['aop']:
                components['aop'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['AOP']['Info']['Path'], "encrypted": False}
            
            if self.required_components['maggie']:
                components['maggie'] = {"path": 'Firmware/Maggie/AppleMaggieFirmwareImage.im4p', "encrypted": False}

            if self.required_components['liquiddetect']:
                components['liquiddetect'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['Liquid']['Info']['Path'], "encrypted": False}

            if self.required_components["multitouch"]:
                components['multitouch'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['Multitouch']['Info']['Path'], "encrypted": False}

            if self.required_components["audiocodec"]:
                components['audiocodec'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['AudioCodecFirmware']['Info']['Path'], "encrypted": False}

            if self.required_components["isp"]:
                components['isp'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['ISP']['Info']['Path'], "encrypted": False}

            if self.required_components["homer"]:
                components['homer'] = {"path": self.manifest['BuildIdentities'][i]['Manifest']['Homer']['Info']['Path'], "encrypted": False}

        for x in components:
            if '/' in components[x]['path']:
                component_file = components[x]['path'].split('/')

                components[x]['file'] = component_file[len(component_file) - 1]
            else:
                components[x]['file'] = components[x]['path']

        return components

class RestoreManifest(object):
    def __init__(self, manifest, device, boardconfig):
        super().__init__()

        self.device = device
        self.manifest = plistlib.load(manifest)
        self.boardconfig = boardconfig

    def fetch_platform(self):
        for x in range(0, len(self.manifest['DeviceMap'])):
            if self.manifest['DeviceMap'][x]['BoardConfig'] == self.boardconfig:
                return self.manifest['DeviceMap'][x]['Platform'][1:]