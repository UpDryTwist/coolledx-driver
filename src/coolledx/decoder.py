"""Class for decoding the traffic."""

# Command byte constants
CMD_MUSIC = 0x01
CMD_TEXT = 0x02
CMD_IMAGE = 0x03
CMD_ANIMATION = 0x04
CMD_ICON = 0x05
CMD_MODE = 0x06
CMD_SPEED = 0x07
CMD_BRIGHTNESS = 0x08
CMD_SWITCH = 0x09
CMD_TRANSFER = 0x0A
CMD_INVERT_DISPLAY = 0x0C
CMD_CLEAR_MAYBE = 0x0D
CMD_SHOW_ICON = 0x11
CMD_POWER_DOWN = 0x12
CMD_POWER_ON = 0x13
CMD_INVERT_OR_SOMETHING = 0x15
CMD_INITIALIZE = 0x23

# Protocol constants
PROTOCOL_END_BYTE = 0x03
ESCAPE_PREFIX = 0x02
ESCAPE_OFFSET = 0x04


class CoolCommand:
    """Class for decoding traffic for purposes of debugging/analysis."""

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
    ) -> None:
        """Initialize the command decoder."""
        self.read_from_raw(raw_command_bytes)
        self.is_send = is_send
        self.source = source
        self.dest = dest
        self.handle = handle

    def read_from_raw(self, raw_command_bytes: bytearray) -> None:
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
        if raw_command_bytes[-1] != PROTOCOL_END_BYTE:
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
            if raw_command_bytes[i] == ESCAPE_PREFIX:
                decoded.append(raw_command_bytes[i + 1] - ESCAPE_OFFSET)
                i += 2
            else:
                decoded.append(raw_command_bytes[i])
                i += 1
        return decoded

    def action_string(self) -> str:
        """Get the action string for the command."""
        if len(self.command) == 0:
            return "NA"

        # Map command bytes to action strings
        command_map = {
            CMD_MUSIC: "Music",
            CMD_TEXT: "Text",
            CMD_IMAGE: "Image",
            CMD_ANIMATION: "Animation",
            CMD_ICON: "Icon",
            CMD_MODE: "Mode",
            CMD_SPEED: "Speed",
            CMD_BRIGHTNESS: "Brightness",
            CMD_SWITCH: "Switch",
            CMD_TRANSFER: "Transfer",
            CMD_INVERT_DISPLAY: "Invert Display",
            CMD_CLEAR_MAYBE: "Clear Maybe",
            CMD_SHOW_ICON: "Show Icon",
            CMD_POWER_DOWN: "Power Down",
            CMD_POWER_ON: "Power On",
            CMD_INVERT_OR_SOMETHING: "Invert Or Something",
            CMD_INITIALIZE: "Initialize",
        }

        return command_map.get(self.command[0], f"Unknown {self.command[0]}")

    def __str__(self) -> str:
        """Return string representation of the command."""
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
