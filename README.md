
# croutonremapkeys

A quick wrapper for using [evdevremapkeys](https://github.com/philipl/evdevremapkeys) on the Pixelbook, though it may be useful on other chromebooks as well.

The Pixelbook contains an extra KEY_ASSISTANT key between left control and alt, where many keyboards have a Windows/Super key, as well as a KEY_CONTROLPANEL at the top  right. X has a keycode limit of 255, far less than the 583 and 579 values our keys have. Meanwhile, remapping them in one of the usual methods loses their function in Chrome OS.

Hence this script: we use Philip Langdale's excellent [evdevremapkeys](https://github.com/philipl/evdevremapkeys) daemon as a module and swap  between two key remapping configurations depending on if Chrome OS or a 
(non-xiwi) X11 window is active, allowing us to use the Assistant and top-right Control Panel key in both environments.

By default, KEY_ASSISTANT is mapped to KEY_COMPOSE/Menu, chosen since it's often set to Hyper and Super is unavailable due to being Search.
KEY_CONTROLPANEL is mapped to KP_DOT/KP_Delete, since recent thinkpad keyboards have delete in that spot, and no numpad means it's certainly free.

## How to use
Install the requirements, then run it as root before X11 grabs the keyboard. 

## Requirements

* Python >= 3.4 (for [asyncio](https://docs.python.org/3/library/asyncio.html))
* [python-daemon](https://pypi.python.org/pypi/python-daemon) >= 2.1.2
* [Python evdev binding](https://pypi.python.org/pypi/evdev) >= 0.7.0
* [pyxdg](https://pypi.python.org/pypi/pyxdg) > 0.25
* [PyYAML](https://pypi.python.org/pypi/PyYAML) >= 3.12
* [pyinotify](https://pypi.python.org/pypi/pyinotify) >=0.9.6
* [evdevremapkeys](https://github.com/philipl/evdevremapkeys) >= 0.1
````