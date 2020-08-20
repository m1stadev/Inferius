from resources import ipsw

device = input('device: ')
version = input('version: ')
ipsw.find_bundle(device, version, 'yes')
