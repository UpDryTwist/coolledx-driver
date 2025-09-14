
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/UpDryTwist/coolledx-driver/graphs/commit-activity)
[![PyPI download month](https://img.shields.io/pypi/dm/coolledx.svg)](https://pypi.python.org/pypi/coolledx-driver/)
[![PyPI version fury.io](https://badge.fury.io/py/coolledx.svg)](https://pypi.python.org/pypi/coolledx-driver/)
[![Documentation Status](https://readthedocs.org/projects/coolledx-driver/badge/?version=latest)](http://coolledx-driver.readthedocs.io/?badge=latest)
[![PR welcome issues still open](https://badgen.net/https/pr-welcome-badge.vercel.app/api/badge/UpDryTwist/coolledx-driver)](https://github.com/UpDryTwist/coolledx-driver/issues?q=archived:false+is:issue+is:open+sort:updated-desc+label%3A%22help%20wanted%22%2C%22good%20first%20issue%22)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![buymecoffee](https://img.shields.io/badge/-buy_me_a%C2%A0coffee-gray?logo=buy-me-a-coffee)](https://www.buymeacoffee.com/updrytwist)

# CoolLEDX Driver

This package implements a Python driver for the CoolLEDX LED strips (i.e., at least
some of those strips that are controlled by the CoolLED1248 app). The strips receive
commands via Bluetooth, and can generally be programmed to display text (which is
actually just a rendered image of the text), images, or animations. You can get these
strips pretty cheaply on AliExpress -- just be sure that you see a picture of the
CoolLED1248 app on the product page, as this driver won't work with any other sort of
strip. That said, they're pretty ubiquitous, at least at the time of this writing (
December 2024).

HOWEVER - be aware that the company has come out with a next generation (apparently),
which identifies as CoolLEDM - and this driver will not work with those strips. If you
have one, and are keen to reverse engineer the protocol, I'd be happy to implement it!
See below for some thoughts/tools for reverse engineering (I started, then just ran out
of
further exploration time).

## Usage

You need to have a functioning Bluetooth device. This package
uses [Bleak](https://github.com/hbldh/bleak)
for all its Bluetooth interactions, so you should be able to use any system supported
by Bleak . . . (I've run on Windows 11 and a Raspberry Pi 4).

### Using a container

You can build a Docker container to run this. Build using "make docker-build".

Running the container as of this moment will run tweak_sign.py (ultimately, I'll
be modifying it to start a service, listening on a message queue). Pass the parameters
to tweak_sign.py as you would if you were running it from the command line.

You can use the utility scripts in the docker_scripts folder to run the container
and call the utility functions appropriately. See an example of using the container
in the utils/process-android-capture.ps1 script, for example.

## Roadmap

* [ ] Write some bare-bones documentation, at least
* [ ] Add a simple REST listener app to allow driving this remotely
* [ ] Push the built docker container to a public repo

## Credits and Sources

#### Main Kudos

This project could not possibly exist without the work done
by [CrimsonClyde](https://git.team23.org/CrimsonClyde)
in reverse engineering the CoolLEDX protocol
at [LED FaceShields](https://git.team23.org/CrimsonClyde/led-faceshields). Much
of the code in this project is directly derived from that code, and almost all of the
insights were from that work. That repository has a bunch of useful information about
the underlying protocol.

#### The Source?

I believe that these LEDs are made
by [Juntong Technology](http://www.jotus-tech.com/en/). I think that
the app itself is made by some 3rd party. I sent an email to the contact at Juntong, but
never got a reply, so not sure. If anyone has a contact, I'd love to get connected, as I
really like their strips!

For source code related to the app, which was helpful in some questions I had about
the protocol (but, honestly, not too much there, and a headache to read), you could try:

* [iOS App (Crosby) Source](https://gitee.com/juntong-iOS/CROSBY_Combine/blob/master/CROSBY_Combine/Classess/Tools/BluetoothManager.m)
* [Some other source that seems to poke the device](https://gitee.com/ifdef/WxBLETools/blob/master/utils/ble.js)

I haven't been able to find any source or implementations for the CoolLEDM - I'd like
that even more than any more CoolLEDX documentation!

#### Sniffing the CoolLED1248 App

For some of my protocol analysis, I found it useful to do the following:

* Turn on BLE logging on my Android phone (under developer options) to save a log
  capture. Be sure to turn it on right before you start the capture, then turn it off
  immediately, so that you're not collecting a ton of junk information.
* Run the CoolLED1248 app and send commands to the LED strip
* Pull the log file from the phone to my PC using the ADB interface
* Analyze it with Wireshark (just put a filter on the MAC address of the LED strip)

This helped me get over some spots where I was a bit lost in the handshakes, or making
some bad assumptions about what was or was not working.

I wound up automating pulling the log file from the phone and breaking out the relevant
packets using utils/process-android-capture.ps1 (and the associated Python decrypter
in utils/bt_analyzer.py). If you follow the steps above to create a log file on your
Android, then connect your phone to your PC (with adb enabled, and Docker running), and
run:

```aiignore
utils/process-android-capture.ps1 -CoolledMac XX:XX:XX:XX:XX:XX
```

That'll give you a nice dump of the chatter between the app and the LED strip.

## Panel Communication

CoolLED1248<br>
Versions 2.x of the Android app can import and export JT files. If you have problems
importing or with other functions, try version 2.1.4.

### PC Image / Animation Creation

If you want to use your PC to create .jt files, check out the JT-Edit repository:
https://github.com/auc0le/JT-Edit

### CoolLEDX Driver Installation - no Docker

To install the CoolLEDX driver on your system:<br>

1. clone the repository to your PC.<br>

       git clone https://github.com/UpDryTwist/coolledx-driver.git

2. From the coolledx-driver folder, copy the coolledx folder to your python library

       cd /yourpath/coolledx-driver/
       cp -a coolledx /home/<yourusername>/.local/lib/python3.8/site-packages/.

3. Install bleak

       pip install bleak

4. If you get this error when trying to run commands from the coolledx driver,

       ImportError: cannot import name 'StrEnum' from 'enum' (/usr/lib/python3.8/enum.py)

   install StrEnum and edit the coolledx/__init__.py file so StrEnum is imported from
   strenum instead of enum

       python3 -m pip install StrEnum

   <pre>
   #---then edit the first few lines of coolledx/__init__.py file----
   #from enum import IntEnum, StrEnum
   from enum import IntEnum
   from strenum import StrEnum
   #-----------------------------------------------------------------
   </pre>

### CoolLEDX Driver Installation - Docker

You can skip all that by just building the Docker container. I'm not currently pushing
it to a common repo (on my to do list). But you can build it yourself by modifying
the repository at the top of the Makefile to point to your repo and then running:

       make docker-build

See examples in the docker_scripts folder for how to run the container and call the
utility functions.

### Using the CoolLEDX Driver

<b>To send commands to the panel:</b>

1. Change to the coolledx-driver directory and use scan.py to find your MAC address.

       python3 utils/scan.py
   <pre>
   --response---
   Scanning for 10.0 seconds (change duration with -t) . . .
   --------------------------------------------------------------------------------
   Device: CoolLEDX (XX:XX:XX:XX:XX:XX), RSSI: -61
   Height: 16, Width: 32
   </pre>

2. Use utils/tweak_sign.py to send commands to the panel.

       python3 utils/tweak_sign.py x
   <pre>
   --response---
   usage: tweak_sign.py [-h] [-a [ADDRESS]] [-t TEXT] [-s SPEED] [-b BRIGHTNESS] [-c COLOR]
                    [-C BACKGROUND_COLOR] [-j START_COLOR_MARKER] [-k END_COLOR_MARKER] [-f FONT]
                    [-H FONT_HEIGHT] [-l LOG] [-o ONOFF] [-m MODE] [-i IMAGE] [-n ANIMATION]
                    [-N ANIMATION_SPEED] [-w WIDTH_TREATMENT] [-g HEIGHT_TREATMENT]
                    [-z HORIZONTAL_ALIGNMENT] [-y VERTICAL_ALIGNMENT] [-jt JTFILE]
   tweak_sign.py: error: unrecognized arguments: xxx
   </pre>

<b>To send an image to the panel:</b>

        python3 utils/tweak_sign.py -a YOUR:MAC:FROM:SCAN:PY -i yourimage.png

<b>To send a JT file to the panel:</b>

        python3 utils/tweak_sign.py -a YOUR:MAC:FROM:SCAN:PY -jt myjtfile.jt

## CoolLEDM

So . . . this works pretty well with the CoolLEDX strips, but there's a new version out,
and the CoolLEDM strips don't follow the same protocol (related, but not the same). You
can follow along with the issue raised.

I got a CoolLEDM strip, and started to reverse engineer the protocol - really just got
far-enough to realize that it was different, and then ran out of time. Here are some
hints
if you want to take it further (I'll probably also poke at it a bit here and there over
the winter).

### Sniffing the traffic

See above for hints on sniffing the traffic between the CoolLED1248 app and the LED
strip.
In essence:

1. Turn on BLE logging on your Android phone (under developer options)
2. Run the CoolLED1248 app and send commands to the LED strip
3. Turn off BLE logging (so you don't get a ton of junk)
4. Run the utils/process-android-capture.ps1 script to pull the log file from your phone
   and extract the relevant packets.

### What I know so far

Here's what I can tell so far:

* The overall protocol (0x01 to start, length, command, 0x03 to end, with 0x02
  encryption)
  is the same.
* Almost none of the actual commands appear to be the same.
* To send text to the sign, it looks as though the processing goes something like this:
    * Process the text into an image buffer (as done in the CoolLEDX)
    * Then send a "text" command to the sign (command 0x02), which probably contains
      some
      kind of checksum regarding the image buffer. The sign will respond back with
      either
      a 0x00 (indicating that it needs the image), or a 0x01 (indicating that it has the
      image already cached and doesn't need it resent).
* Unfortunately, the command formats for both (text 0x02 and image 0x03) are too opaque
  for me to easily figure out.
* Another changed one, for example, is the Music (0x01) command - the CoolLEDX uses 16
  bytes (8 x height + 8 x color), where the CoolLEDM uses 8 bytes (I'm guessing that
  it's half of each byte for each).

### APK Reverse Engineering

It would be pretty cool if someone would reverse engineer the APK to figure this out.
Just saying.

### Here's some sample dump . . .

Turned on the music bars, then sent "foo", "bar", "foo", "foobar", "aaa", "bbb", "
aaa", "aab"
(you can see where the repeated values didn't require sending an image)

```aiignore
Filtering /tmp/btsnoop_hci.log on ( bthci_acl.dst.bd_addr == ff:00:00:04:25:ab or bthci_acl.src.bd_addr == ff:00:00:04:25:ab )  and ( btatt.characteristic_uuid16 == 0x2aa6 or btatt.service_uuid16 == 0xfff0 or btatt.service_uuid16 == 0xfff1)
-> CoolLEDM (Clear Maybe) [0x00000059]
0D 15 15 15 15 15 15 15 00
<- MyPhone (Clear Maybe) [0x00000059]
0D 00
-> CoolLEDM (Unknown {self.command[0]}) [0x00000059]
1F
<- MyPhone (Unknown {self.command[0]}) [0x00000059]
1F 01 FF 00 01 00 03
-> CoolLEDM (Music) [0x00000059]
01 05 03 01 02 03 02 01 01 00
-> CoolLEDM (Music) [0x00000059]
01 05 0B 02 02 01 00 00 01 00
-> CoolLEDM (Music) [0x00000059]
01 05 02 02 01 00 01 01 01 02
-> CoolLEDM (Clear Maybe) [0x00000059]
0D 28 28 28 28 28 28 28 00
<- MyPhone (Clear Maybe) [0x00000059]
0D 00
-> CoolLEDM (Unknown {self.command[0]}) [0x00000059]
1F
<- MyPhone (Unknown {self.command[0]}) [0x00000059]
1F 01 FF 00 01 00 03
-> CoolLEDM (Unknown {self.command[0]}) [0x00000059]
1F
<- MyPhone (Unknown {self.command[0]}) [0x00000059]
1F 01 FF 00 01 00 03
-> CoolLEDM (Text) [0x00000059]
02 D3 4D D5 94 00 00 00 7E 00 01
<- MyPhone (Text) [0x00000059]
02 00
-> CoolLEDM (Image) [0x00000059]
03 00 00 00 00 51 00 00 00 51 B6 ED 15 02 01 ED
10 22 06 EA 19 60 FF 00 10 02 F7 03 00 00 03 7F
00 1B 08 0A 09 01 01 F7 11 E1 52 F7 11 ED 11 1E
03 09 05 00 36 04 FF 02 7F FE FF FE 84 02 80 F3
00 C0 08 00 24 00 F8 03 FC 06 F7 06 04 02 4C 01
06 06 03 FC 1B 01 F8 44 0F 01 F8 6E
<- MyPhone (Image) [0x00000059]
03 00 00 00 00
-> CoolLEDM (Text) [0x00000059]
02 F5 66 07 5D 00 00 00 82 00 01
<- MyPhone (Text) [0x00000059]
02 00
-> CoolLEDM (Image) [0x00000059]
03 00 00 00 00 59 00 00 00 59 B6 ED 15 02 01 ED
10 22 06 EA 19 60 FF 00 10 02 F7 03 00 00 03 7F
00 1D 0A 0A 09 01 01 F7 11 E1 56 F7 11 ED 11 1E
03 09 05 00 3A 80 7F 00 FF FE FF FE 04 02 3C 03
EF 07 FE 03 FC ED 10 7C 04 FE FB 04 86 4E 03 07
FC 03 FE 00 A7 02 00 00 42 02 3B 01 00 66 01 06
00 10 00 DE
<- MyPhone (Image) [0x00000059]
03 00 00 00 00
-> CoolLEDM (Text) [0x00000059]
02 E3 F7 70 FC 00 00 00 C0 00 01
<- MyPhone (Text) [0x00000059]
02 00
-> CoolLEDM (Image) [0x00000059]
03 00 00 00 00 81 00 00 00 81 B6 ED 15 02 01 ED
10 28 06 EA 19 60 FF 00 10 02 F7 03 00 00 06 6F
00 39 08 0A 15 00 09 01 1A 02 C2 ED 10 8E F7 11
ED 11 24 03 09 05 00 72 FF 04 02 7F FE FF FE 84
02 E7 80 00 C0 08 00 2A 00 F8 03 FC EF 06 06 04
02 52 01 06 06 03 E7 FC 01 F8 4A 0F 5C 01 80 00
FF FC 3F 00 52 03 04 02 07 FE 03 FC BE ED 10 7C
04 FE 04 86 8C 03 07 7F FC 03 FE 00 02 00 00 80
02 7A 79 01 00 A4 01 06 00 03 00 F1
<- MyPhone (Image) [0x00000059]
03 00 00 00 00
-> CoolLEDM (Text) [0x00000059]
02 D3 4D D5 94 00 00 00 7E 00 01
<- MyPhone (Text) [0x00000059]
02 01
-> CoolLEDM (Text) [0x00000059]
02 AF B0 13 05 00 00 00 82 00 01
<- MyPhone (Text) [0x00000059]
02 00
-> CoolLEDM (Image) [0x00000059]
03 00 00 00 00 42 00 00 00 42 B6 ED 15 02 01 ED
10 22 06 EA 19 60 FF 00 10 02 F7 03 00 00 03 7F
00 1D 0A 0A 09 01 01 F7 11 E1 56 F7 11 ED 11 1E
03 09 05 00 3A 00 DF 7C 04 FE 04 86 3A 03 07 FC
8F 03 FE 00 02 ED 10 37 0F 49 0F 02 FE
<- MyPhone (Image) [0x00000059]
03 00 00 00 00
-> CoolLEDM (Text) [0x00000059]
02 34 29 DF AD 00 00 00 82 00 01
<- MyPhone (Text) [0x00000059]
02 00
-> CoolLEDM (Image) [0x00000059]
03 00 00 00 00 44 00 00 00 44 B6 ED 15 02 01 ED
10 22 06 EA 19 60 FF 00 10 02 F7 03 00 00 03 7F
00 1D 0A 0A 09 01 01 F7 11 E1 56 F7 11 ED 11 1E
03 09 05 00 3A 80 7F 00 FF FE FF FE 04 02 3C 03
3F 07 FE 03 FC 00 00 36 0F 48 0F 03 03 FC 6B
<- MyPhone (Image) [0x00000059]
03 00 00 00 00
-> CoolLEDM (Text) [0x00000059]
02 AF B0 13 05 00 00 00 82 00 01
<- MyPhone (Text) [0x00000059]
02 01
-> CoolLEDM (Text) [0x00000059]
02 3A 74 BE 92 00 00 00 82 00 01
<- MyPhone (Text) [0x00000059]
02 00
-> CoolLEDM (Image) [0x00000059]
03 00 00 00 00 50 00 00 00 50 B6 ED 15 02 01 ED
10 22 06 EA 19 60 FF 00 10 02 F7 03 00 00 03 7F
00 1D 0A 0A 09 01 01 F7 11 E1 56 F7 11 ED 11 1E
03 09 05 00 3A 00 DF 7C 04 FE 04 86 3A 03 07 FC
CF 03 FE 00 02 ED 10 37 0F 00 80 7F 00 FF FE FF
FE 04 02 64 03 0F 07 FE 03 FC 6D
<- MyPhone (Image) [0x00000059]
03 00 00 00 00

```
