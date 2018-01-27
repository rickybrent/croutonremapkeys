#!/usr/bin/env python3
#
# Copyright (c) 2018 Ricky Brent
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import asyncio
import evdevremapkeys
import functools
import os
import pyinotify
import subprocess
import time
from collections import namedtuple

load_config_file = evdevremapkeys.load_config

"""Check the active display and change the key remap on change."""


class CroutonCycleHandler(pyinotify.ProcessEvent):
    def my_init(self, config):
        self.config = config
        self.config_cros = load_config_file('config-cros.yaml')
        self.config_x11 = load_config_file('config-x11.yaml')
        self.process_IN_MODIFY(None)

    def reload_config(self):
        self.apply_config(load_config_file('config-cros.yaml'),
                          self.config_cros)
        self.apply_config(load_config_file('config-x11.yaml'), self.config_x11)

    def process_IN_MODIFY(self, event):
        # Checking 'croutoncycle display' includes xiwi instances, so:
        try:
            self.x11_active = subprocess.check_output(
                'croutoncycle list | grep -e "^:[0-9]*\*[^\/]*$"', shell=True)
        except:
            self.x11_active = False
        if (self.x11_active):
            self.apply_config(self.config_x11)
        else:
            self.apply_config(self.config_cros)

    def apply_config(self, update, dest=None):
        update_map = {}
        for device in update['devices']:
            name = device.get('input_name', None)
            phys = device.get('input_phys', None)
            fn = device.get('input_fn', None)
            update_map[(name, phys, fn)] = device['remappings']
        dest = self.config if not dest else dest
        for device in dest['devices']:
            name = device.get('input_name', None)
            phys = device.get('input_phys', None)
            fn = device.get('input_fn', None)
            device['remappings'].clear()
            if (name, phys, fn) in update_map:
                device['remappings'].update(update_map[(name, phys, fn)])


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    config = load_config_file('config-x11.yaml')
    loop = asyncio.get_event_loop()
    croutonlockcmd = ("echo -n $(cat `which croutoncycle` | grep "
                      "CROUTONLOCKDIR= | cut -d '=' -f 2 | tr -d \"'\")")
    croutonlockdir = subprocess.check_output(croutonlockcmd, shell=True)
    crouton_display_path = croutonlockdir.decode("utf-8") + "/display"
    wm = pyinotify.WatchManager()
    loop = asyncio.get_event_loop()
    notifier = pyinotify.AsyncioNotifier(wm, loop)
    handler = functools.partial(CroutonCycleHandler, config=config)
    wm.watch_transient_file(crouton_display_path, pyinotify.IN_MODIFY, handler)

    evdevremapkeys.load_config = lambda z: config
    ArgsShim = namedtuple("ArgsShim", "config_file")
    while True:
        try:
            evdevremapkeys.run_loop(ArgsShim(None))
        except OSError as e:
            print("Another instance has grabbed the input device, waiting...")
            time.sleep(3)
        else:
            break
