#!/usr/bin/env python3

import argparse
import os
import shutil
from resources import extract
import sys

assert ('darwin' in sys.platform), "This script can only be ran on macOS. Please run this on a macOS computer."

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ipsw', help='specify IPSW')
parser.add_argument('-r', '--ramdisk', help='find and print ramdisk name')
parser.add_argument('-v', '--verbose', help='print verbose output', action='store_true')
args = parser.parse_args()
if args.ipsw:
    if args.verbose:
        print(f'extracting IPSW at this -> {args.ipsw}')
        extract.extract_ipsw(args.ipsw, 'yes')
    else:
        print(f'extracting IPSW at this -> {args.ipsw}')
        extract.extract_ipsw(args.ipsw)

if args.ramdisk:
    extract.find_ramdisk()
