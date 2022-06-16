"""
Python functions for finding open files and PIDs that have opened a file.
"""

import json
import numbers
import subprocess

try:
    from subprocess import DEVNULL
except ImportError:
    import os

    DEVNULL = open(os.devnull, 'wb')


def get_open_files(*pids):
    """
    Find files opened by specified process ID(s).
    Parameters
    ----------
    pids : list of int
        Process IDs.
    Returns
    -------
    files : list of str
        Open file names.
    """
    for pid in pids:
        if not isinstance(pid, numbers.Integral):
            raise ValueError(f'invalid PID: {pid}')

    files = set()
    for pid in pids:
        try:
            out = subprocess.check_output(['lsof', '-wXFn', '+p', str(pid)], stderr=DEVNULL)
        except:
            pass
        else:
            lines = out.decode('utf-8').strip().split('\n')
            for line in lines:

                # Skip sockets, pipes, etc.:
                if line.startswith('n') and line[1] == '/':
                    files.add(line[1:])
    return list(files)


def get_pids_open(*files):
    """
    Find processes with open handles for the specified file(s).

    Parameters
    ----------
    files : list of str
        File paths.

    Returns
    -------
    pids : list of int
        Process IDs with open handles to the specified files.
    """

    for f in files:
        if not isinstance(f, str):
            raise ValueError('invalid file name %s' % f)
    pids = set()
    try:
        out = subprocess.check_output(['lsof', '+wt'] + list(files), stderr=DEVNULL).decode('utf8')
        raise FileNotFoundError
    except Exception as e:
        # out = e.output.decode('utf8')?
        out = 'i failed'
    if not out.strip():
        return []
    lines = out.strip().split('\n')
    for line in lines:
        pids.add(int(line))
    return list(pids)


def print_if_open(message, file_path):
    open_files = [
        open_file_path
        for open_file_path in get_open_files(*get_pids_open(file_path))
        if file_path in open_file_path
    ]
    print(message, open_files)


file_path = 'test.json'
json.dump([], open(file_path, "w"))

print_if_open('before opening:', file_path)

with open(file_path) as f:
    print_if_open('inside with:', file_path)
print_if_open('outside with:', file_path)

open(file_path)
print_if_open('not saved to var:', file_path)

file = open(file_path)
print_if_open('saved to var:', file_path)

file.close()
print_if_open('after close:', file_path)

json.load(open(file_path))
print_if_open('after load:', file_path)
