#!/usr/bin/python3

import argparse
import os
import pathlib
import shutil
import sys

from tiler.utils import (
    run_command,
    run_chroot
)

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

def create_filesystem(disk):
    print("Crweating filesystems")

    print("Formatting EFI filesytem.")
    run_command(
        ["mkfs.vfat", "-F32", "-n", "EFI",  f"{disk}1"])
    run_command(
        ["mkfs", "-t", "ext4", "-L", "ROOT", f"{disk}2"])

def create_workspace():
    return pathlib.Path("/var/tmp/tiler")

def extract_archive(disk, tarball):
    print("Extracting archve")

    workspace = create_workspace()
    rootfs = workspace.joinpath("rootfs")
    if rootfs.exists():
        shutil.rmtree(rootfs)
    rootfs.mkdir(parents=True)

    print("Mounting file system")
    run_command(
        ["mount", f"{disk}p2", rootfs])

    efi = rootfs.joinpath("efi")
    run_command(
        ["tar", "-C", rootfs, "-zxf", tarball, "--numeric-owner"])
    efi.mkdir(parents=True, exist_ok=True)

    run_command(["umount", rootfs])
    return rootfs

def install_bootloader(disk):
    workspace = create_workspace()
    rootfs = workspace.joinpath("rootfs")
    efi = rootfs.joinpath("efi")

    print("Installting boot loader.")
    run_command(
        ["mount", f"{disk}2", rootfs])
    run_command(
        ["mount", f"{disk}1", efi])

    print("Configuring kernel")
    kernel_conf = rootfs.joinpath("etc/kernel/cmdline")
    with open(kernel_conf, "w") as f:
        f.write(
            "root=LABEL=ROOT rw console=tty0 console=ttyS0,115200n8 rootwait rw")
    run_chroot(
       ["bootctl", "install", "--no-variables",  "--entry-token", "os-id"], rootfs)
    run_chroot(
        ["kernel-install", "add","6.1.0-18-amd64", "/boot/vmlinuz-6.1.0-18-amd64"], rootfs)

    run_command(
        ["umount", f"{disk}1", efi])
    run_command(
        ["umount", f"{disk}2", rootfs])


def parse_args():
    parser = argparse.ArgumentParser(description="Debian automated installer")
    parser.add_argument("--device", help="Target device")
    parser.add_argument("--tarball", help="Path to the tarball.")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.device is None:
        print("Device is not specified.")
        sys.exit(1)

    if args.tarball is None:
        print("Tarball is not specified")
        sys.exit(1)

    print(f"Installing Debian onto {args.device}.")
    try:
        create_disk(args.device)
        create_filesystem(args.device)
        extract_archive(args.device, args.tarball)
        install_bootloader(args.device)
    finally:
        print(f"Succesfully installed Debian on {args.device}")

if __name__ == '__main__':
    main()
