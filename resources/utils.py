from datetime import datetime
import glob
import os
import requests
import shutil

current_date = datetime.now().strftime('%m-%d-%y')

def log(text, is_verbose):
    current_time = datetime.now()
    current_time = current_time.strftime('%I:%M:%S %p')
    if is_verbose:
        print(text)

    text = text.replace('\n', f'\n[{current_time}] ')
    if text == 'Inferius Log' or text == 'Inferius Restore Log':
        if os.path.isfile(f'resources/Inferius-{current_date}.log'):
            os.remove(f'resources/Inferius-{current_date}.log')

    with open(f'resources/Inferius-{current_date}.log', 'a') as f:
            f.write(f'[{current_time}] {text}\n')

def cleanup(rm_log=None):
    if os.path.isdir('work/'):
        shutil.rmtree('work/')
    
    if rm_log:
        for f in glob.glob('resources/*.log'):
            os.remove(f)

def check_internet():
    try:
        requests.get('https://google.com', timeout=5)
        return True
    except(requests.ConnectionError, requests.Timeout):
        return False