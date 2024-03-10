import os
import subprocess


def run_command(args, data=None, env=None, capture=False, shell=False):
    try:
        if not capture:
            stdout = None
            stderr = None
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        stdin = subprocess.PIPE
        sp = subprocess.Popen(args, stdout=stdout,
                              stderr=stderr, stdin=stdin,
                              env=env, shell=shell, universal_newlines=True)
        (out, err) = sp.communicate(data)
    except OSError as e:
        raise Exception(f"failed to run cmd: {args}")
    # Just ensure blank instead of none
    if not out and capture:
       out = out
    if not err and capture:
       err = err
    return (out, err)

def run_chroot(args, rootfs, data=None, env=None, capture=False, shell=False):
    try:
        cmd = [
             "bwrap",
             "--bind", rootfs, "/",
             "--bind", f"{rootfs}/efi" , "/efi",
             "--bind", "/sys/firmware/efi/efivars", "/sys/firmware/efi/efivars",
             "--proc", "/proc",
             "--dev-bind", "/dev", "/dev",
             "--dir", "/run",
             "--bind", "/tmp", "/tmp",
             "--bind", "/sys", "/sys",
             "--share-net",
             "--die-with-parent",
             "--chdir", "/",
        ]
        cmd += args
        (out, err) = run_command(cmd,
                    data=data,
                    env=env,
                    capture=capture,
                    shell=shell)
    except OSError as e:
        raise Exception(f"Failed to run chroot command: {args}")
    if not out and capture:
        out = out
    if not err and capture:
        err = err
    return (out, err)
