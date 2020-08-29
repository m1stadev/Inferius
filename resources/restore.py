import subprocess

def is_cellular(device_identifier):
    non_cellular_devices = ['ipad6,11', 'ipad7,5', 'ipad7,11', 'ipod7,1', 'ipod9,1', 'ipad4,1', 'ipad5,3', 'ipad6,7', 'ipad6,3', 'ipad7,1', 'ipad7,3', 'ipad4,4', 'ipad4,7', 'ipad5,1']
    device_identifier = device_identifier.lower()
    if device_identifier in non_cellular_devices:
        return False
    else:
        return True

def restore(ipsw_path, is_cellular, keep_data, verbose=None):
    if is_cellular:
        if keep_data:
            print('Requested to keep data, please note this is experimental!')
            subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2 -u --latest-sep --latest-baseband --use-pwndfu {ipsw_path}', shell=True)
        else:
            subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2 --latest-sep --latest-baseband --use-pwndfu {ipsw_path}', shell=True)
    else:
        if keep_data:
            print('Requested to keep data, please note this is experimental!')
            subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2 -u --latest-sep --latest-baseband --use-pwndfu {ipsw_path}', shell=True)
        else:
            subprocess.run(f'./resources/bin/futurerestore -t work/ipsw/blob.shsh2 --latest-sep --no-baseband --use-pwndfu {ipsw_path}', shell=True)