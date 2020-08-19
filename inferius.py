#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import extract 


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ipsw', help='specify IPSW')
parser.add_argument('-r', '--ramdisk', help='find and print ramdisk name')
args = parser.parse_args()
if args.ipsw:
    print(f'extracting IPSW at this -> {args.ipsw}')
    extract.extract_ipsw(args.ipsw)

if args.ramdisk:
    extract.find_ramdisk()
