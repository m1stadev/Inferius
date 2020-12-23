import bsdiff4
import sys
import usb

class Bundle(object):
    def __init__(self, device, ipsw_path):
        super().__init__()

        self.device = device
        self.ipsw = ipsw_path

    def apply_patches(self):
        with open(f'{bundle}/Info.json', 'r') as f:
            bundle_data = f.read()

        #TODO: actually do this lol