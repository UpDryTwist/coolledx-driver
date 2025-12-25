"""
Basic protocol implementation for CoolLED devices.

This is the protocol that is used by the CoolLEDX and related devices.  It is
responsible for encoding and decoding the commands that are sent to the device.
"""

from __future__ import annotations


class BasicProtocol:
    """Basic protocol implementation for CoolLED devices."""


    def create_command(self, raw_data: bytearray) -> bytearray:
        """Create the command.  In the basic protocol, the command protocol is 
        0x01 [data] 0x03 to handle the framing."""
        extended_data = bytearray().join(
            [len(raw_data).to_bytes(2, byteorder="big"), raw_data],
        )
        return bytearray().join([b"\x01", self.escape_bytes(extended_data), b"\x03"])