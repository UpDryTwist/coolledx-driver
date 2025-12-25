"""
CoolLED hardware definitions.

Describes the different CoolLED hardware we know. This is all pieced together
without any documentation.  If you have documentation, please share!

Generally, there are five classes of hardware, as far as I can tell:
- Basic:  This is the original CoolLED.  It has a fixed size, and a simple protocol.
- CoolLEDX:  This is the next generation of the CoolLED.  Simple protocol, varying matrix sizes.
- CoolLEDM:  This is the next generation of the CoolLEDX.  Uses advanced protocol. varying matrix sizes.
- CoolLEDU:  This is the next generation of the CoolLEDM.  Uses advanced protocol, varying matrix sizes.
- CoolLEDUD:  This is a specialized version of the CoolLEDU for bike applications.  Same protocol as CoolLEDU.
- CoolLEDMX:  This might be the more expensive commercial signs?.  Uses advanced protocol, different handler.
- CoolLEDUX:  A lot more functionality.  Extends the protocols.  I'll never have one (unless you send me one), so not worrying about it!
"""

from .message_handler import MessageHandler, CoolLEDXMessageHandler, CoolLEDMMessageHandler, CoolLEDUMessageHandler, CoolLEDMXMessageHandler, CoolLEDUXMessageHandler
from .commands import COLOR_TYPE_MONO

class CoolLED:
    """Base class for CoolLED hardware definitions."""

    device_width: int
    device_height: int
    device_color_mode: int
    device_firmware_version: int

    @classmethod
    def get_class_for_string(cls, device_type: str) -> type["CoolLED"]:
        """Get the class for the given device type."""
        if device_type == "CoolLED":
            return CoolLEDOriginal
        if device_type == "CoolLEDA":
            return CoolLEDA
        if device_type == "CoolLEDX":
            return CoolLEDX
        if device_type == "CoolLEDS":
            return CoolLEDS
        if device_type == "CoolLEDM":
            return CoolLEDM
        if device_type == "CoolLEDU":
            return CoolLEDU
        if device_type == "CoolLEDUD" or device_type == "iLedBike":
            return CoolLEDUD
        if device_type == "CoolLEDMX":
            return CoolLEDMX
        if device_type == "CoolLEDUX":
            return CoolLEDUX
        raise ValueError(f"Unknown device type: {device_type}")

    def __init__(self, device_width: int, device_height: int, device_color_mode: int, device_firmware_version: int) -> None:
        """Initialize the hardware definition."""
        self.device_width = device_width
        self.device_height = device_height
        self.device_color_mode = device_color_mode
        self.device_firmware_version = device_firmware_version

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Default to CoolLEDX."""
        return CoolLEDXMessageHandler()

    def is_implemented(self) -> bool:
        """Check if the hardware is implemented."""
        return False
    
    def implementation_note(self) -> str:
        """Get the implementation note for the hardware."""
        return "This device has not been implemented - contributions welcome!"
    
    def is_variable_height_width(self) -> bool:
        """Check if the hardware has variable height and width."""
        return True

    def get_device_width(self) -> int:
        """Get the device width."""
        return self.device_width

    def get_device_height(self) -> int:
        """Get the device height."""
        return self.device_height

    def get_device_color_mode(self) -> int:
        """Get the device color mode."""
        return self.device_color_mode

    def get_device_firmware_version(self) -> int:
        """Get the device firmware version."""
        return self.device_firmware_version

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

class CoolLEDOriginal(CoolLED):
    """CoolLEDOriginal hardware implementation.
    Original is a fixed 12x48 matrix.  We don't currently do anything to support it.
    Characteristics:
    - Single color support only
    - No password verification
    - Single data transmission protocol
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDX message handler."""
        return CoolLEDXMessageHandler()
    
    def is_variable_height_width(self) -> bool:
        """Check if the hardware has variable height and width."""
        return False
    
    def get_device_height(self):
        """Return fixed 12pixel height."""
        return 12

    def get_device_width(self):
        """Return fixed 48pixel width."""
        return 48

    def get_device_color_mode(self) -> int:
        """Return fixed mono color mode."""
        return COLOR_TYPE_MONO

class CoolLEDA(CoolLED):
    """CoolLEDA hardware implementation.
    Characteristics:
    - Fixed 16x32 matrix
    - No password verification
    - Simplified protocol for specific applications
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDX message handler."""
        return CoolLEDXMessageHandler()
    
    def is_variable_height_width(self) -> bool:
        """Check if the hardware has variable height and width."""
        return False
    
    def get_device_height(self):
        """Return fixed 16pixel height."""
        return 16;

    def get_device_width(self):
        """Return fixed 32pixel width."""
        return 32;
class CoolLEDX(CoolLED):
    """CoolLEDX hardware implementation."""

    def is_implemented(self) -> bool:
        """Check if the hardware is implemented."""
        return True
    
    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDX message handler."""
        return CoolLEDXMessageHandler()

class CoolLEDS(CoolLED):
    """CoolLEDS hardware implementation. (S = Secure)
    Characteristics:
    - Color capability detection
    - Always requires password verification
    - Multiple matrix sizes
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDX message handler."""
        return CoolLEDXMessageHandler()
    
    def implementation_note(self) -> str:
        """Get the implementation note for the hardware."""
        return "This device has not been implemented - requires special security handling.  Contributions welcome!"

class CoolLEDM(CoolLED):
    """CoolLEDM hardware implementation.
    Characteristics:
    - Variables sizes: 16x32 through to 32x more than 192
    - Firmware version tracking
    - Advanced matrix configurations
    - Program data transmission support
    - Color capability detection
    - Limited OTA update capability
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDM message handler."""
        return CoolLEDMMessageHandler()

class CoolLEDU(CoolLED):
    """CoolLEDU hardware implementation. (U = ?)
    Characteristics:
    - Full color support
    - Firmware version tracking
    - Advanced matrix configurations including 20-row and 24-row variants
    - Program data transmission
    - OTA update support
    - Local microphone support detection
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDU message handler."""
        return CoolLEDUMessageHandler()

class CoolLEDUD(CoolLED):
    """CoolLEDUD hardware implementation. (UD = Urban Display (bikes))
    Characteristics:
    - Specialized for bike/urban applications
    - Device name: iLedBike
    - Full color support
    - Firmware version tracking
    - Rugged design considerations
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDU message handler."""
        return CoolLEDUMessageHandler()

class CoolLEDMX(CoolLED):
    """CoolLEDMX hardware implementation. (MX = matrix eXtended)
    Characteristics:
    - Matrix extended capabilities
    - Seven color support
    - Firmware version tracking
    - Advanced program data transmission
    - Enhanced matrix configurations
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDMX message handler."""
        return CoolLEDMXMessageHandler()

class CoolLEDUX(CoolLED):
    """CoolLEDUX hardware implementation. (UX = ultra eXtended)
    Characteristics:
    - Full color support
    - Advanced firmware version tracking with per-device tracking
    - Dynamic package size configuration
    - Comprehensive OTA update support
    - Advanced program data transmission
    - Clock, date, scoreboard, and timer features
    """

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDUX message handler."""
        return CoolLEDUXMessageHandler()