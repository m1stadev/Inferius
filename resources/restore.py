import subprocess


def send_ibss_ibec(processor):
    if processor.lower() == 's5l8960' or 't8015':
        with open('work/empty_file', 'w') as f:
            f.close()

    irecovery_path = 'resources/bin/irecovery'

    subprocess.run(
        (irecovery_path,
         '-f',
         'work/empty_file'),
        stdout=subprocess.PIPE)

    subprocess.run(
        (irecovery_path,
         '-f',
         'work/ipsw/ibss.img4'),
        stdout=subprocess.PIPE)

    subprocess.run(
        (irecovery_path,
         '-f',
         'work/ipsw/ibec.img4'),
        stdout=subprocess.PIPE)

    if processor.lower() == 't8010' or 't8015':
        subprocess.run(
            (irecovery_path,
             '-c',
             'go'),
            stdout=subprocess.PIPE)


def is_cellular(device_identifier):
    non_cellular_devices = [
        'iPad6,11', 'iPad7,5', 'iPad7,11', 'iPod7,1', 'iPod9,1', 'iPad4,1', 'iPad5,3',
        'iPad6,7', 'iPad6,3', 'iPad7,1', 'iPad7,3', 'iPad4,4', 'iPad4,7', 'iPad5,1']

    device_identifier = device_identifier.lower()

    if device_identifier in non_cellular_devices:
        return False
    else:
        return True


def restore(ipsw_path, is_cellular, keep_data):
    futurerestore_path = 'resources/bin/futurerestore'
    shsh_path = 'work/ipsw/blob.shsh2'

    if is_cellular:
        if keep_data:
            print('Requested to keep data, please note this is experimental!')
            subprocess.run(
                (futurerestore_path,
                 '-t',
                 shsh_path,
                 '-u',
                 '--latest-sep',
                 '--latest-baseband',
                 ipsw_path))
        else:
            subprocess.run(
                (futurerestore_path,
                 '-t',
                 shsh_path,
                 '--latest-sep',
                 '--latest-baseband',
                 ipsw_path))
    else:
        if keep_data:
            print('Requested to keep data, please note this is experimental!')
            subprocess.run(
                (futurerestore_path,
                 '-t',
                 shsh_path,
                 '-u',
                 '--latest-sep',
                 '--latest-baseband',
                 ipsw_path))
        else:
            subprocess.run(
                (futurerestore_path,
                 '-t',
                 shsh_path,
                 '--latest-sep',
                 '--no-baseband',
                 ipsw_path))
