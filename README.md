# Licht

The software for my living room light, server running on a Raspberry Pi (`server.py`).
Controlled via socket through the `licht.py` script.

Uses `asyncio`, runs on Python 3.4, which is the current version on Raspbian 8. No external python dependencies.

Requires [WiringPI](http://wiringpi.com) to be installed on the system (`apt install wiringpi`)
