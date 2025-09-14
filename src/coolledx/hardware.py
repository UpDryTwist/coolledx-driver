"""
This describes the different CoolLED hardware we know.  I have no idea what's going
on, as flying without documentation, but it appears that the command set for
the CoolLEDX is different from the set for the CoolLEDM . . . (?)
"""


class CoolLED:
    def cmdbyte_music(self) -> int:
        return 0x01

    def cmdbyte_text(self) -> int:
        return 0x02

    def cmdbyte_image(self) -> int:
        return 0x03

    def cmdbyte_animation(self) -> int:
        return 0x04

    def cmdbyte_icon(self) -> int:
        return 0x05

    # Unproven - reference in docs somewhere
    # On the CoolLedM, this was sent with parameter 1F
    # before sending text.
    def cmdbyte_buttonoff(self) -> int:
        return 0x05

    def cmdbyte_mode(self) -> int:
        return 0x06

    def cmdbyte_speed(self) -> int:
        return 0x07

    def cmdbyte_brightness(self) -> int:
        return 0x08

    def cmdbyte_switch(self) -> int:
        return 0x09

    # Unproven - reference in docs somewhere
    def cmdbyte_xfer(self) -> int:
        return 0x0A

    # Works on CoolLEDM
    def cmdbyte_invertdisplay(self) -> int:
        return 0x0C

    # Saw this on a CoolLEDM before sending text.
    # Was followed by 28 28 28 28 28 28 28 00
    def cmdbyte_clearmaybe(self) -> int:
        return 0x0D

    # Unproven - reference in docs somewhere
    def cmdbyte_showicon(self) -> int:
        return 0x11

    # Unproven - reference in docs somewhere
    def cmdbyte_powerdown(self) -> int:
        return 0x12

    # Unproven - this is supposed to turn on and initialize
    def cmdbyte_buttonon(self) -> int:
        return 0x13

    # Unproven - reference in docs somewhere
    def cmdbyte_invertorsomething(self) -> int:
        return 0x15

    # Saw the app send this to CoolLEDM and get back 01 ff 00 01 00
    def cmdbyte_requestsomething(self):
        return 0x1F

    # This one seems to actually work, at least on a CoolLEDM
    def cmdbyte_initialize(self) -> int:
        return 0x23


class CoolLEDX(CoolLED):
    pass


class CoolLEDM(CoolLED):
    pass
