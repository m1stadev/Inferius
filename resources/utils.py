from datetime import datetime
import os
import requests
import shutil

raw_datetime = datetime.now()
formatted_time = raw_datetime.strftime('%I:%M:%S %p')
formatted_date = raw_datetime.strftime('%m-%d-%y')

def log(text):
    with open(f'resources/Inferius-{formatted_date}.log', 'a') as f:
            f.write(f'[{formatted_time}] {text}\n')

def print_and_log(text, is_verbose):
    if is_verbose:
        print(text)

    with open(f'resources/Inferius-{formatted_date}.log', 'a') as f:
        f.write(f'[{formatted_time}] {text}\n')

def cleanup(is_verbose):
    if is_verbose == 'exit':
       print_and_log('[VERBOSE] Cleaning out work/ directory', False) 
    elif is_verbose:
        print_and_log('[VERBOSE] Cleaning out work/ directory', is_verbose)
    

    if os.path.isdir('work/'):
        shutil.rmtree('work/')

def check_internet():
    try:
        requests.get('https://google.com', timeout=5)
        return True
    except(requests.ConnectionError, requests.Timeout):
        return False