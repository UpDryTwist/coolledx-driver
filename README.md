
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/UpDryTwist/coolledx-driver/graphs/commit-activity)
[![PyPI download month](https://img.shields.io/pypi/dm/coolledx-driver.svg)](https://pypi.python.org/pypi/coolledx-driver/)
[![PyPI version fury.io](https://badge.fury.io/py/coolledx-driver.svg)](https://pypi.python.org/pypi/coolledx-driver/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/coolledx-driver.svg)](https://pypi.python.org/pypi/coolledx-driver/)
[![Documentation Status](https://readthedocs.org/projects/coolledx-driver/badge/?version=latest)](http://coolledx-driver.readthedocs.io/?badge=latest)
[![PR welcome issues still open](https://badgen.net/https/pr-welcome-badge.vercel.app/api/badge/UpDryTwist/coolledx-driver)](https://github.com/UpDryTwist/coolledx-driver/issues?q=archived:false+is:issue+is:open+sort:updated-desc+label%3A%22help%20wanted%22%2C%22good%20first%20issue%22)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![buymecoffee](https://img.shields.io/badge/-buy_me_a%C2%A0coffee-gray?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/updrytwist)

# CoolLEDX Driver

This package implements a Python driver for the CoolLEDX LED strips (i.e., those strips
that are controlled by the CoolLED1248 app).  The strips receive commands via Bluetooth,
and can generally be programmed to display text (which is actually just a rendered image
of the text), images, or animations.  You can get these strips pretty cheaply on AliExpress
-- just be sure that you see a picture of the CoolLED1248 app on the product page, as this
driver won't work with any other sort of strip.  That said, they're pretty ubiquitous, at
least at the time of this writing (December 2023).

## Usage

You need to have a functioning Bluetooth device.  This package uses [Bleak](https://github.com/hbldh/bleak)
for all its Bluetooth interactions, so you should be able to use any system supported
by Bleak . . . but it hasn't been tested on anything other than Windows 11 (and soon
Ubuntu on a Pi).

## Roadmap

* [ ] Write some bare-bones documentation, at least
* [ ] Ensure this is tested out on a Raspberry Pi (my end target device)
* [ ] Add a simple REST listener app to allow driving this remotely


## Credits and Sources

#### Main Kudos

This project could not possibly exist without the work done by [CrimsonClyde](https://git.team23.org/CrimsonClyde)
in reverse engineering the CoolLEDX protocol at [LED FaceShields](https://git.team23.org/CrimsonClyde/led-faceshields).  Much
of the code in this project is directly derived from that code, and almost all of the
insights were from that work.  That repository has a bunch of useful information about
the underlying protocol.

#### The Source?

I believe that these LEDs are made by [Juntong Technology](http://www.jotus-tech.com/en/).  I think that
the app itself is made by some 3rd party.  I sent an email to the contact at Juntong, but
never got a reply, so not sure.  If anyone has a contact, I'd love to get connected, as I
really like their strips!

For source code related to the app, which was helpful in some questions I had about
the protocol (but, honestly, not too much there, and a headache to read), you could try:

* [iOS App (Crosby) Source](https://gitee.com/juntong-iOS/CROSBY_Combine/blob/master/CROSBY_Combine/Classess/Tools/BluetoothManager.m)
* [Some other source that seems to poke the device](https://gitee.com/ifdef/WxBLETools/blob/master/utils/ble.js)

#### Sniffing the CoolLED1248 App

For some of my protocol analysis, I found it useful to do the following:
* Turn on BLE logging on my Android phone (under developer options) to save a log capture.
  Be sure to turn it on right before you start the capture, then turn it off immediately,
  so that you're not collecting a ton of junk information.
* Run the CoolLED1248 app and send commands to the LED strip
* Pull the log file from the phone to my PC using the ADB interface
* Analyze it with Wireshark (just put a filter on the MAC address of the LED strip)

This helped me get over some spots where I was a bit lost in the handshakes, or making
some bad assumptions about what was or was not working.
