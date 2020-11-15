import sys

class Device(object):
    def __init__(self, device_identifier, version):
        super().__init__()

        self.device = device_identifier
        self.cellular = self.has_baseband()
        self.maggie = self.has_maggie()
        self.homer = self.has_homer()
        self.version = version
        self.template = self.get_wiki_template()

    def has_baseband(self):
        if self.device.startswith('iPhone'):
            return True

        elif self.device.startswith('iPod'):
            return False

        elif self.device.startswith('iPad'):
            cellular_ipads = ['iPad4,2', 'iPad4,3', 'iPad5,4', 'iPad11,4', 'iPad13,2', 'iPad6,8', 'iPad6,4', 'iPad7,2', 'iPad7,4', 'iPad8,3', 'iPad8,4', 'iPad8,7', 'iPad8,8', 'iPad8,10', 'iPad8,12', 'iPad4,5', 'iPad4,6', 'iPad4,8', 'iPad4,9', 'iPad5,2', 'iPad11,2']
            if self.device in cellular_ipads:
                return True
            else:
                return False
    
    def has_maggie(self):
        maggie_devices = ['iPhone9,1', 'iPhone9,2', 'iPhone9,3', 'iPhone9,4', 'iPhone10,1', 'iPhone10,2', 'iPhone10,3', 'iPhone10,4', 'iPhone10,5', 'iPhone10,6']
        if self.device in maggie_devices:
            return True
        return False

    def has_homer(self):
        homer_devices = ['iPhone9,1', 'iPhone9,2', 'iPhone9,3', 'iPhone9,4']
        if self.device in homer_devices:
            return True
        return False

    def get_wiki_template(self):
        a7_devices = ['iPad4,1', 'iPad4,2', 'iPad4,3', 'iPad4,4', 'iPad4,5', 'iPad4,6', 'iPad4,7', 'iPad4,8', 'iPad4,9', 'iPhone6,1', 'iPhone6,2']
        a8_devices = ['iPad5,1', 'iPad5,2', 'iPad5,3', 'iPad5,4', 'iPhone7,1', 'iPhone7,2', 'iPod7,1']
        a9_devices = ['iPad6,11', 'iPad6,12', 'iPad6,3', 'iPad6,4', 'iPad6,7', 'iPad6,8', 'iPhone8,1', 'iPhone8,2', 'iPhone8,4']
        a10_devices = ['iPad7,1', 'iPad7,2', 'iPad7,11', 'iPad7,12', 'iPad7,5', 'iPad7,6', 'iPhone9,1', 'iPhone9,2', 'iPhone9,3', 'iPhone9,4', 'iPod9,1', 'iPad7,1', 'iPad7,2', 'iPad7,3', 'iPad7,4']
        a11_devices = ['iPhone10,1', 'iPhone10,2', 'iPhone10,4', 'iPhone10,5', 'iPhone10,3', 'iPhone10,6']

        self.required_components = {}

        if self.device in a7_devices or self.device in a8_devices:
            if self.cellular:
                wiki_template = 'resources/templates/a7a8_cellular.txt'
            else:
                wiki_template = 'resources/templates/a7a8_nocellular.txt'

        elif self.device in a9_devices:
            sys.exit('[ERROR] A9 devices are not currently supported. Exiting...')

        elif self.device in a10_devices:
            if self.cellular:
                wiki_template = 'resources/templates/a10_cellular.txt'
            else:
                wiki_template = 'resources/templates/a10_nocellular.txt'
            
            if self.homer:
                wiki_template = f'{wiki_template[:-4]}_maggie_homer.txt' # All devices with Homer also have Maggie
            
        elif self.device in a11_devices:
            wiki_template = 'resources/templates/a11_cellular_maggie.txt'

            if int(self.version[:2]) >= 13:
                wiki_template = f'{wiki_template[:-4]}_adc.txt'

        if '_cellular' in wiki_template:
            self.required_components["baseband"] = True
        else:
            self.required_components["baseband"] = False

        if '_maggie' in wiki_template:
            self.required_components["maggie"] = True
            self.required_components["liquiddetect"] = True
        else:
            self.required_components["maggie"] = False
            self.required_components["liquiddetect"] = False

        if '_homer' in wiki_template:
            self.required_components["homer"] = True
        else:
            self.required_components["homer"] = False

        if '_adc' in wiki_template:
            self.required_components["isp"] = True
        else:
            self.required_components["isp"] = False

        if self.device in a9_devices or self.device in a10_devices or self.device in a11_devices:
            self.required_components["aop"] = True
        else:
            self.required_components["aop"] = False

        if self.device in a11_devices:
            self.required_components["audiocodec"] = True
            self.required_components["multitouch"] = True
        else:
            self.required_components["audiocodec"] = False
            self.required_components["multitouch"] = False

        return wiki_template