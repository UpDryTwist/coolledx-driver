"""
Class for decoding the traffic.
"""


class CoolCommand:
    """
    Class for decoding traffic for purposes of debugging/analysis.
    """

    length: int
    command: bytearray
    action: str
    is_send: bool
    source: str
    dest: str
    handle: int

    def __init__(
        self,
        is_send: bool,
        source: str,
        dest: str,
        handle: int,
        raw_command_bytes: bytearray,
    ):
        self.read_from_raw(raw_command_bytes)
        self.is_send = is_send
        self.source = source
        self.dest = dest
        self.handle = handle

    def read_from_raw(self, raw_command_bytes: bytearray):
        """
        Decode the overall command string we've received.  We're receiving a hex-encoded
        string, of the form "XX:XX:XX:XX...".  The first byte should always be 01, and
        the last byte should always be 03.  The second and third bytes are the length
        of the command (big-endian).  The rest of the bytes are the command itself.

        The numbers in the string are encoded.  A 0x02 byte means that the next byte
        should be interpreted as value - 0x04 -- so for example, "02:05" would be 0x01,
        "02:06" would be 0x02, and so on.

        This stores the value of the raw_command_str in self.length and self.command.
        """
        raw_command_bytes = self.decode_command(raw_command_bytes)
        if raw_command_bytes[0] != 0x01:
            raise ValueError(
                f"Invalid packet structure (opening byte != 0x01): {raw_command_bytes[0]:02X}",
            )
        # The last byte should be 0x03
        if raw_command_bytes[-1] != 0x03:
            raise ValueError(
                f"Invalid packet structure (closing byte != 0x03): {raw_command_bytes[-1]:02X}",
            )

        self.length = raw_command_bytes[1] * 256 + raw_command_bytes[2]
        self.command = raw_command_bytes[3:-1]
        self.action = self.action_string()

    def decode_command(self, raw_command_bytes: bytearray) -> bytearray:
        """
        Decode the command bytes.  A byte of 0x02 means that the next byte should be
        interpreted as value - 0x04 -- so for example, "02:05" would be 0x01, "02:06"
        would be 0x02, and so on.
        """
        decoded = bytearray()
        i = 0
        while i < len(raw_command_bytes):
            if raw_command_bytes[i] == 0x02:
                decoded.append(raw_command_bytes[i + 1] - 0x04)
                i += 2
            else:
                decoded.append(raw_command_bytes[i])
                i += 1
        return decoded

    def action_string(self) -> str:
        if len(self.command) == 0:
            return "NA"
        if self.command[0] == 0x01:
            return "Music"
        if self.command[0] == 0x02:
            return "Text"
        if self.command[0] == 0x03:
            return "Image"
        if self.command[0] == 0x04:
            return "Animation"
        if self.command[0] == 0x05:
            return "Icon"
        if self.command[0] == 0x06:
            return "Mode"
        if self.command[0] == 0x07:
            return "Speed"
        if self.command[0] == 0x08:
            return "Brightness"
        if self.command[0] == 0x09:
            return "Switch"
        if self.command[0] == 0x0A:
            return "Transfer"
        if self.command[0] == 0x0C:
            return "Invert Display"
        if self.command[0] == 0x0D:
            return "Clear Maybe"
        if self.command[0] == 0x11:
            return "Show Icon"
        if self.command[0] == 0x12:
            return "Power Down"
        if self.command[0] == 0x13:
            return "Power On"
        if self.command[0] == 0x15:
            return "Invert Or Something"
        if self.command[0] == 0x23:
            return "Initialize"
        return "Unknown {self.command[0]}"

    def __str__(self):
        lines = []
        if self.is_send:
            lines.append(f"-> {self.dest} ({self.action}) [{self.handle}]")
        else:
            lines.append(f"<- {self.dest} ({self.action}) [{self.handle}]")
        for i in range(0, len(self.command), 16):
            chunk = self.command[i : i + 16]
            # Convert each byte to two-digit uppercase hex and join with spaces
            line = " ".join(f"{byte:02X}" for byte in chunk)
            lines.append(line)
        # Join all lines with a newline character
        return "\n".join(lines)
