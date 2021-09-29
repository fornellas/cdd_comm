#!/usr/bin/env python3

# MIT License

# Copyright (c) Facebook, Inc. and its affiliates.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import pty
import signal
import subprocess
import sys
import threading

master_pty_fd, slave_pty_fd = pty.openpty()
read_data = []


def master_pty_fd_reader():
    while True:
        try:
            data = os.read(master_pty_fd, 1024)
        except OSError:
            return
        else:
            if data:
                read_data.append(data)
            else:
                return


master_pty_fd_reader_thread = threading.Thread(target=master_pty_fd_reader)

master_pty_fd_reader_thread.start()

pid = None


def handler(signal_number, frame):
    if not pid:
        return
    os.kill(pid, signal_number)


signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGHUP, handler)

try:
    popen = subprocess.Popen(
        sys.argv[1:],
        stdin=subprocess.DEVNULL,
        stdout=slave_pty_fd,
        stderr=slave_pty_fd,
    )
except FileNotFoundError as e:
    print(str(e), file=sys.stderr)
    os.close(slave_pty_fd)
    master_pty_fd_reader_thread.join()
    sys.exit(127)

pid = popen.pid

returncode = popen.wait()

os.close(slave_pty_fd)

master_pty_fd_reader_thread.join()

if returncode:
    for data in read_data:
        os.write(sys.stdout.fileno(), data)
    sys.exit(returncode)