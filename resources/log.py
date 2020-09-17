import os
from datetime import datetime

raw_datetime = datetime.now()
formatted_time = raw_datetime.strftime('%I:%M:%S %p')
formatted_date = raw_datetime.strftime('%m-%d-%y')

def log_to_file(text):

    if os.path.isfile(f'resources/{formatted_date}.log'):
        os.remove(f'resources/{formatted_date}.log')

    with open(f'resources/{formatted_date}.log', 'w+') as f:
        f.write(f'[{formatted_time}] {text}\n')