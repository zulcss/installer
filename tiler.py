#!/usr/bin/python3

import argparse
import sys

from tiler.utils import run_command

def create_disk(disk):
    print(f"Setting up partitions on {disk}")

    run_command(["parted", "-s", disk, "mklabel", "gpt"])
    run_command(
        ["parted", "-s", disk, "mkpart", "EFI", "FAT32", "1MB", "500MB"])
    run_command(
        ["parted", "-s", disk, "set", "1", "esp", "on"])
    run_command(
        ["parted", "-s", disk, "set", "1", "boot", "on"])
    run_command(
        ["parted", "-s", disk, "mkpart", "ROOT", "ext4", "500Mb", "100%"])

def parse_args():
    parser = argparse.ArgumentParser(description="Debian automated installer")
    parser.add_argument("--device", help="Target device")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.device is None:
        print("Device is not specified.")
        sys.exit(1)

    print(f"Installing Debian onto {args.device}.")
    try:
        create_disk(args.device)
    finally:
        print(f"Succesfully installed Debian on {args.device}")

if __name__ == '__main__':
    main()
