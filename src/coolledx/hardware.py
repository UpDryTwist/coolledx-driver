"""
CoolLED hardware definitions.

Describes the different CoolLED hardware we know. I have no idea what's going
on, as flying without documentation, but it appears that the command set for
the CoolLEDX is different from the set for the CoolLEDM.
"""


class CoolLED:
    """Base class for CoolLED hardware definitions."""

    def cmdbyte_music(self) -> int:
        """Get the music command byte."""
        return 0x01

    def cmdbyte_text(self) -> int:
        """Get the text command byte."""
        return 0x02

    def cmdbyte_image(self) -> int:
        """Get the image command byte."""
        return 0x03

    def cmdbyte_animation(self) -> int:
        """Get the animation command byte."""
        return 0x04

    def cmdbyte_icon(self) -> int:
        """Get the icon command byte."""
        return 0x05

    # Unproven - reference in docs somewhere
    # On the CoolLedM, this was sent with parameter 1F
    # before sending text.
    def cmdbyte_buttonoff(self) -> int:
        """Get the button off command byte."""
        return 0x05

    def cmdbyte_mode(self) -> int:
        """Get the mode command byte."""
        return 0x06

    def cmdbyte_speed(self) -> int:
        """Get the speed command byte."""
        return 0x07

    def cmdbyte_brightness(self) -> int:
        """Get the brightness command byte."""
        return 0x08

    def cmdbyte_switch(self) -> int:
        """Get the switch command byte."""
        return 0x09

    # Unproven - reference in docs somewhere
    def cmdbyte_xfer(self) -> int:
        """Get the transfer command byte."""
        return 0x0A

    # Works on CoolLEDM
    def cmdbyte_invertdisplay(self) -> int:
        """Get the invert display command byte."""
        return 0x0C

    # Saw this on a CoolLEDM before sending text.
    # Was followed by 28 28 28 28 28 28 28 00
    def cmdbyte_clearmaybe(self) -> int:
        """Get the clear maybe command byte."""
        return 0x0D

    # Unproven - reference in docs somewhere
    def cmdbyte_showicon(self) -> int:
        """Get the show icon command byte."""
        return 0x11

    # Unproven - reference in docs somewhere
    def cmdbyte_powerdown(self) -> int:
        """Get the power down command byte."""
        return 0x12

    # Unproven - this is supposed to turn on and initialize
    def cmdbyte_buttonon(self) -> int:
        """Get the button on command byte."""
        return 0x13

    # Unproven - reference in docs somewhere
    def cmdbyte_invertorsomething(self) -> int:
        """Get the invert or something command byte."""
        return 0x15

    # Saw the app send this to CoolLEDM and get back 01 ff 00 01 00
    def cmdbyte_requestsomething(self) -> int:
        """Get the request something command byte."""
        return 0x1F

    # This one seems to actually work, at least on a CoolLEDM
    def cmdbyte_initialize(self) -> int:
        """Get the initialize command byte."""
        return 0x23


class CoolLEDX(CoolLED):
    """CoolLEDX hardware implementation."""


class CoolLEDM(CoolLED):
    """CoolLEDM hardware implementation."""
