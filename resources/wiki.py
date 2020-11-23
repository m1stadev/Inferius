import mwclient
import os
import sys

class Wiki(object):
    def __init__(self, device, buildid, version, codename, components):
        super().__init__()

        self.device = device
        self.buildid = buildid
        self.codename = codename
        self.components = components
        self.version = version

        self.site = mwclient.Site('www.theiphonewiki.com')
        self.page = self.site.pages[f'{self.codename}_{self.buildid}_({self.device})']

        self.wikikeys = self.get_wiki_keys()

    def login_info(self, wiki_user, wiki_pass): self.login = [wiki_user, wiki_pass]

    def get_wiki_keys(self):
        if not self.page.exists:
            return False
        wikikeys = {}

        data = self.page.text().replace(' ', '').replace('|', '').splitlines()
        wiki_version = self.page.text().replace('|', '').splitlines()[1].split('=')[1][1:].replace('[Golden MasterGM]', '[Golden Master|GM]')
        for x in data:
            if x == '' or x == '}}' or x == '{{keys':
                data.pop(data.index(x))
                continue

        for x in data:
            new_str = x.split('=')
            try:
                wikikeys[new_str[0].lower()] = new_str[1]
            except IndexError:
                continue

        wikikeys['version'] = wiki_version

        return wikikeys

    def make_keypage(self, keys, template, ipsw_url):
        with open(template, 'r+') as f:
            wiki_template = f.read()

        wiki_keys = wiki_template
        wiki_keys = wiki_keys.replace('{BUILDID}', self.buildid)
        wiki_keys = wiki_keys.replace('{DEVICEIDENTIFIER}', self.device)
        wiki_keys = wiki_keys.replace('{URL}', ipsw_url)
        wiki_keys = wiki_keys.replace('{CODENAME}', self.codename)
        wiki_keys = wiki_keys.replace('{ROOTFS}', self.components['rootfs']['file'][:-4])
        wiki_keys = wiki_keys.replace('{RESTORERAMDISK}', self.components['restoreramdisk']['file'][:-4])
        wiki_keys = wiki_keys.replace('{UPDATERAMDISK}', self.components['updateramdisk']['file'][:-4])
        wiki_keys = wiki_keys.replace('{IBSSKEY}', keys['ibss']['key'])
        wiki_keys = wiki_keys.replace('{IBSSIV}', keys['ibss']['iv'])
        wiki_keys = wiki_keys.replace('{IBECKEY}', keys['ibec']['key'])
        wiki_keys = wiki_keys.replace('{IBECIV}', keys['ibec']['iv'])
        wiki_keys = wiki_keys.replace('{IBOOTKEY}', keys['iboot']['key'])
        wiki_keys = wiki_keys.replace('{IBOOTIV}', keys['iboot']['iv'])
        wiki_keys = wiki_keys.replace('{LLBKEY}', keys['llb']['key'])
        wiki_keys = wiki_keys.replace('{LLBIV}', keys['llb']['iv'])
        wiki_keys = wiki_keys.replace('{APPLELOGO}', self.components['applelogo']['file'])
        wiki_keys = wiki_keys.replace('{BATTERYCHARGING0}', self.components['batterycharging0']['file'])
        wiki_keys = wiki_keys.replace('{BATTERYCHARGING1}', self.components['batterycharging1']['file'])
        wiki_keys = wiki_keys.replace('{BATTERYFULL}', self.components['batteryfull']['file'])
        wiki_keys = wiki_keys.replace('{BATTERYLOW0}', self.components['batterylow0']['file'])
        wiki_keys = wiki_keys.replace('{BATTERYLOW1}', self.components['batterylow1']['file'])
        wiki_keys = wiki_keys.replace('{GLYPHPLUGIN}', self.components['glyphplugin']['file'])
        wiki_keys = wiki_keys.replace('{DEVICETREE}', self.components['devicetree']['file'])
        wiki_keys = wiki_keys.replace('{KERNELCACHE}', self.components['kernelcache']['file'])
        wiki_keys = wiki_keys.replace('{LLB}', self.components['llb']['file'])
        wiki_keys = wiki_keys.replace('{RECOVERYMODE}', self.components['recoverymode']['file'])
        wiki_keys = wiki_keys.replace('{SEP}', self.components['sep']['file'])
        wiki_keys = wiki_keys.replace('{IBEC}', self.components['ibec']['file'])
        wiki_keys = wiki_keys.replace('{IBSS}', self.components['ibss']['file'])
        wiki_keys = wiki_keys.replace('{IBOOT}', self.components['iboot']['file'])

        if self.wikikeys:
            if self.wikikeys['sepfirmwareiv'] != 'Unknown':
                wiki_keys = wiki_keys.replace('{SEPIV}', self.wikikeys['sepfirmwareiv'])
                wiki_keys = wiki_keys.replace('{SEPKEY}', self.wikikeys['sepfirmwarekey'])
                wiki_keys = wiki_keys.replace('\n | SEPFirmwareKBAG       = {SEPKBAG}', '')
            else:
                wiki_keys = wiki_keys.replace('{SEPIV}', keys['sep']['iv'])
                wiki_keys = wiki_keys.replace('{SEPKEY}', keys['sep']['key'])
                wiki_keys = wiki_keys.replace('{SEPKBAG}', keys['sep']['kbag'])

            if self.wikikeys['version'] != self.version:
                wiki_keys = wiki_keys.replace('{VERSION}', self.wikikeys['version'])
            else:
                wiki_keys = wiki_keys.replace('{VERSION}', self.version)

        else:
            wiki_keys = wiki_keys.replace('{SEPIV}', keys['sep']['iv'])
            wiki_keys = wiki_keys.replace('{SEPKEY}', keys['sep']['key'])
            wiki_keys = wiki_keys.replace('{SEPKBAG}', keys['sep']['kbag'])
            wiki_keys = wiki_keys.replace('{VERSION}', self.version)

        if '{BASEBANDVER}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{BASEBANDVER}', self.components['baseband']['version'])

        if '{HOMER}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{HOMER}', self.components['homer']['file'])

        if '{MAGGIE}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{MAGGIE}', self.components['maggie']['file'])
        
        if '{AOP}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{AOP}', self.components['aop']['file'])

        if '{MULTITOUCH}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{MULTITOUCH}', self.components['multitouch']['file'])

        if '{AUDIOCODEC}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{AUDIOCODEC}', self.components['audiocodec']['file'])

        if '{ISP}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{ISP}', self.components['isp']['file'])

        if '{LIQUIDDETECT}' in wiki_keys:
            wiki_keys = wiki_keys.replace('{LIQUIDDETECT}', self.components['liquiddetect']['file'])

        return wiki_keys

    def save_keys(self, page):
        os.makedirs(f'keys/{self.device}/{self.version}/{self.buildid}/', exist_ok=True)

        with open(f'keys/{self.device}/{self.version}/{self.buildid}/wiki_keys.txt', 'w') as f:
            f.write(page)

    def upload_to_wiki(self, page_contents):
        try:
            self.site.login(self.login[0], self.login[1])
        except mwclient.errors.LoginError:
            sys.exit('[ERROR] TheiPhoneWiki login information is incorrect, keys cannot be uploaded. Exiting...')

        keypage_text = self.page.text()

        if self.page.exists:
            print(f"[NOTE] iOS {self.version}'s keys for {self.device} are already on the wiki. Continuing...")
            return

        self.page.edit(page_contents, 'Add keys via Criptam')

        print(f"iOS {self.version}'s keys for {self.device} uploaded to TheiPhoneWiki")