"""Commands for the CoolLEDX package."""

import abc
import re
from asyncio import Future
from enum import Enum

from coolledx import (
    DEFAULT_ANIMATION_SPEED,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_COLOR,
    DEFAULT_END_COLOR_MARKER,
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_START_COLOR_MARKER,
    HeightTreatment,
    HorizontalAlignment,
    Mode,
    VerticalAlignment,
    WidthTreatment,
)

from .hardware import CoolLED
from .render import (
    create_animation_payload,
    create_image_payload,
    create_JT_payload,
    create_text_payload,
)

DEFAULT_DEVICE_WIDTH = 96
DEFAULT_DEVICE_HEIGHT = 16


class CoolLedError(Exception):
    """Base class for exceptions in this module."""

    pass


class ErrorCode(Enum):
    """
    Error codes returned by the device.
    """

    UNKNOWN = -1
    SUCCESS = 0x00
    TRANSMISSION_FAILED = 0x01
    DEVICE_ABNORMALITY = 0x02
    DATA_ERROR = 0x03
    DATA_LENGTH_ERROR = 0x04
    DATA_ID_ERROR = 0x05
    DATA_CHECKSUM_ERROR = 0x06

    @staticmethod
    def get_error_code_name(error_code: "int | ErrorCode") -> str:
        """
        Return a human-readable error message for the given error code.
        """
        try:
            return ErrorCode(error_code).name
        except ValueError:
            return f"Unknown error code: {error_code:02X}"


class CommandStatus(Enum):
    """
    Status of the currently executing command
    """

    NOT_STARTED = 0
    TRANSMITTED = 1
    ACKNOWLEDGED = 2
    ERROR = 3


class Command(abc.ABC):
    """Abstract base class for commands."""

    sign_height: int
    sign_width: int
    dimensions_set: bool = False
    command_status: CommandStatus = CommandStatus.NOT_STARTED
    error_code: ErrorCode = ErrorCode.UNKNOWN
    future: Future | None = None
    hardware: CoolLED = CoolLED()

    @abc.abstractmethod
    def get_command_raw_data_chunks(self) -> list[bytearray]:
        """Get the set of commands as a bytearray."""
        pass

    @staticmethod
    def escape_byte(byte: int) -> bytearray:
        """Bytes < 4 need to be escaped with 0x02."""
        if byte < 0x04:
            return bytearray([0x02, byte + 0x04])
        else:
            return bytearray([byte])

    @staticmethod
    def escape_bytes(bytes_to_escape: bytearray) -> bytes:
        data = re.sub(
            re.compile(b"\x02", re.MULTILINE), b"\x02\x06", bytes_to_escape
        )  # needs to be first
        data = re.sub(re.compile(b"\x01", re.MULTILINE), b"\x02\x05", data)
        data = re.sub(re.compile(b"\x03", re.MULTILINE), b"\x02\x07", data)
        return data

    def set_dimensions(self, width: int, height: int) -> None:
        """Set the dimensions of the sign."""
        self.sign_width = width
        self.sign_height = height
        self.dimensions_set = True

    def set_hardware(self, hardware: CoolLED) -> None:
        """Set the hardware type."""
        self.hardware = hardware

    def set_future(self, future: Future) -> None:
        """Set the future for this command."""
        self.future = future

    def set_command_status(self, status: CommandStatus) -> None:
        """Set the status of the command."""
        self.command_status = status

    @property
    def get_device_width(self) -> int:
        return self.sign_width if self.dimensions_set else DEFAULT_DEVICE_WIDTH

    @property
    def get_device_height(self) -> int:
        return self.sign_height if self.dimensions_set else DEFAULT_DEVICE_HEIGHT

    @staticmethod
    def expect_notify() -> bool:
        """
        Should we expect a notification from the device?
        This only applies to commands that send data.
        """
        return True

    @staticmethod
    def is_raw_command() -> bool:
        """
        Is this a raw command, meaning that we shouldn't encode/escape the data?
        """
        return False

    def create_command(self, raw_data: bytearray) -> bytearray:
        """Create the command."""
        extended_data = bytearray().join(
            [len(raw_data).to_bytes(2, byteorder="big"), raw_data]
        )
        return bytearray().join([b"\x01", self.escape_bytes(extended_data), b"\x03"])

    @staticmethod
    def split_bytearray(data: bytearray, chunksize: int) -> list[bytearray]:
        chunks = [data]

        # split the last chunk as long as it is larger than chunksize
        while True:
            i = len(chunks) - 1
            if len(chunks[i]) > chunksize:
                chunks.append(chunks[i][chunksize:])
                chunks[i] = chunks[i][:chunksize]
            else:
                return chunks

    @staticmethod
    def get_xor_checksum(data: bytearray) -> int:
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum

    def chop_up_data(self, data: bytearray, command: int) -> list[bytearray]:
        # split the content into (128-byte) chunks
        raw_chunks = self.split_bytearray(data, 128)

        # add header information to the chunks
        chunks = []
        for chunk_id, raw_chunk in enumerate(raw_chunks):
            # create bytearray of for the content of the chunk including checksum
            formatted_chunk = bytearray()
            # unknown single 0x00 byte TODO
            formatted_chunk += b"\x00"
            # length of the playload before it was split (16-bit)
            formatted_chunk += len(data).to_bytes(2, byteorder="big")
            # current chunk-number (16-bit)
            formatted_chunk += chunk_id.to_bytes(2, byteorder="big")
            # size of the chunk (8-bit)
            formatted_chunk += len(raw_chunk).to_bytes(1, byteorder="big")
            # the data of the chunk
            formatted_chunk += raw_chunk
            # append XOR checksum to make the complete the formatted chunk
            formatted_chunk.append(self.get_xor_checksum(formatted_chunk))
            # Prepend our command byte for each chunk
            chunks.append(
                bytearray().join(
                    [command.to_bytes(1, byteorder="big"), formatted_chunk]
                )
            )
        return chunks

    def get_command_chunks(self) -> list[bytearray]:
        """Get the command as a bytearray."""
        raw_data_chunks = self.get_command_raw_data_chunks()
        if self.is_raw_command():
            return raw_data_chunks
        else:
            chunks = [self.create_command(x) for x in raw_data_chunks]
            return chunks

    def get_command_hexstr(self, append_newline: bool = True) -> str:
        """Get the command as a hex string."""
        hex_string = ""
        for chunk in self.get_command_chunks():
            hex_string += chunk.hex() + ("\n" if append_newline else "")
        return hex_string

    def truncated_command(self) -> str:
        """
        Return a string representation of the command that has been truncated to
        32 characters.
        """
        hexstr = self.get_command_hexstr(append_newline=False)
        if len(hexstr) > 32:
            hexstr = hexstr[:32] + "..."
        return hexstr

    def __str__(self):
        return f"{self.__class__.__name__}[{self.truncated_command()}]"


class SendRawData(Command):
    """Send raw data to the scroller"""

    data: bytearray

    def __init__(self, data_as_hex: str) -> None:
        self.data = bytearray.fromhex(data_as_hex)

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [self.data]

    @staticmethod
    def is_raw_command() -> bool:
        return True


class Initialize(Command):
    """Initialize the scroller"""

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [bytearray.fromhex(f"{self.hardware.cmdbyte_initialize():02x} 01")]


class SetSpeed(Command):
    """Command to set the speed of the scroller."""

    speed: int

    def __init__(self, speed: int) -> None:
        """Legitimate speeds are 0x00 to 0xFF."""
        if speed < 0x00 or speed > 0xFF:
            raise ValueError(f"Speed must be between 0x00 and 0xFF, not {speed}")
        self.speed = speed

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray.fromhex(f"{self.hardware.cmdbyte_speed():02x} {self.speed:02X}")
        ]


class SetBrightness(Command):
    """Set brightness on the scroller"""

    brightness: int

    def __init__(self, brightness: int) -> None:
        """Legitimate brightness values are 0x00 to 0xFF."""
        if brightness < 0x00 or brightness > 0xFF:
            raise ValueError(
                f"Brightness must be between 0x00 and 0xFF, not {brightness}"
            )
        self.brightness = brightness

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray.fromhex(
                f"{self.hardware.cmdbyte_brightness():02x} {self.brightness:02X}"
            )
        ]


class TurnOnOffApp(Command):
    """Turn on/off the scroller"""

    on: bool

    def __init__(self, on: bool) -> None:
        self.on = on

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        onoff = 0x01 if self.on else 0x00
        return [bytearray.fromhex(f"{self.hardware.cmdbyte_switch():02x} {onoff:02X}")]


class TurnOnOffButton(Command):
    """Turn on/off the scroller"""

    on: bool

    def __init__(self, on: bool) -> None:
        self.on = on

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        onoff = 0x01 if self.on else 0x00
        command = (
            self.hardware.cmdbyte_buttonon()
            if self.on
            else self.hardware.cmdbyte_buttonoff()
        )
        return [bytearray.fromhex(f"{command:02X} {onoff:02X}")]


class ShowChargingAnimation(Command):
    """Show the charging animation"""

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray(self.hardware.cmdbyte_showicon().to_bytes(1, byteorder="big"))
        ]


class InvertDisplay(Command):
    """Invert the display"""

    inverted: bool = False

    def __init__(self, inverted: bool = False) -> None:
        self.inverted = inverted

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray.fromhex(
                f"{self.hardware.cmdbyte_invertdisplay():02x} {self.inverted:02X}"
            )
        ]


class InvertOrSomething(Command):
    """Mirror the display"""

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray(
                self.hardware.cmdbyte_invertorsomething().to_bytes(1, byteorder="big")
            )
        ]


class StartupWithBatteryLevel(Command):
    """Startup with battery level"""

    battery_level: int

    def __init__(self, battery_level: int) -> None:
        """Legitimate battery levels are 0x00 to 0xFF."""
        if battery_level < 0x00 or battery_level > 0xFF:
            raise ValueError(
                f"Battery level must be between 0x00 and 0xFF, not {battery_level}"
            )
        self.battery_level = battery_level

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray.fromhex(
                f"{self.hardware.cmdbyte_initialize():02x} {self.battery_level:02X}"
            )
        ]


class PowerDown(Command):
    """Power down the device"""

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray(self.hardware.cmdbyte_powerdown().to_bytes(1, byteorder="big"))
        ]


class SetMode(Command):
    """Set the text movement style for the scroller"""

    mode: Mode

    def __init__(self, mode: Mode) -> None:
        self.mode = mode

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [
            bytearray.fromhex(f"{self.hardware.cmdbyte_mode():02x} {self.mode:02X}")
        ]


class SetMusicBars(Command):
    """Set music bars:  8 bars of height (byte), each with a color from 1-7"""

    heights: bytearray
    colors: bytearray

    def __init__(self, heights: bytearray, colors: bytearray) -> None:
        if len(heights) != 8:
            raise ValueError(f"Heights must be 8 bytes, not {len( heights )}")
        if len(colors) != 8:
            raise ValueError(f"Colors must be 8 bytes, not {len( colors )}")
        self.heights = heights
        self.colors = colors

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        # At least with the CoolLEDM, this is 8 bytes total being sent.  I'm suspecting
        # that heights and colors are integrated into a half byte each.
        return [
            bytearray.fromhex(
                f"{self.hardware.cmdbyte_music():02x} {self.heights.hex()} {self.colors.hex()}"
            )
        ]


class SetText(Command):
    """Set the text to display"""

    text: str
    default_color: str
    background_color: str
    color_markers: tuple[str | None, str | None] | str = (None, None)
    font: str
    font_height: int
    render_as_text: bool = True
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER

    def __init__(
        self,
        text: str,
        default_color: str = DEFAULT_COLOR,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        color_markers: tuple[str | None, str | None] | str = (
            DEFAULT_START_COLOR_MARKER,
            DEFAULT_END_COLOR_MARKER,
        ),
        font: str = DEFAULT_FONT,
        font_height: int = DEFAULT_FONT_SIZE,
        render_as_text: bool = True,
        width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
        height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
        vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    ) -> None:
        self.text = text
        self.default_color = default_color
        self.background_color = background_color
        self.font = font
        self.font_height = font_height
        self.render_as_text = render_as_text
        self.width_treatment = width_treatment
        self.height_treatment = height_treatment
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment
        self.color_markers = color_markers

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        raw_text = create_text_payload(
            self.text,
            default_color=self.default_color,
            background_color=self.background_color,
            color_markers=self.color_markers,
            font=self.font,
            font_height=self.font_height,
            sign_width=self.get_device_width,
            sign_height=self.get_device_height,
            render_as_text=self.render_as_text,
            width_treatment=self.width_treatment,
            height_treatment=self.height_treatment,
            horizontal_alignment=self.horizontal_alignment,
            vertical_alignment=self.vertical_alignment,
        )
        return self.chop_up_data(
            raw_text,
            self.hardware.cmdbyte_text()
            if self.render_as_text
            else self.hardware.cmdbyte_image(),
        )

    @staticmethod
    def expect_notify() -> bool:
        return True


class SetImage(Command):
    """Set the display image by loading from a file"""

    filename: str
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE
    background_color: str

    def __init__(
        self,
        filename: str,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
        height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
        vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    ) -> None:
        self.filename = filename
        self.background_color = background_color
        self.width_treatment = width_treatment
        self.height_treatment = height_treatment
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        raw_data = create_image_payload(
            self.filename,
            background_color=self.background_color,
            sign_width=self.get_device_width,
            sign_height=self.get_device_height,
            width_treatment=self.width_treatment,
            height_treatment=self.height_treatment,
            horizontal_alignment=self.horizontal_alignment,
            vertical_alignment=self.vertical_alignment,
        )
        return self.chop_up_data(raw_data, self.hardware.cmdbyte_image())

    @staticmethod
    def expect_notify() -> bool:
        return True


class SetAnimation(Command):
    """Set the display to an animation from an animated image file"""

    filename: str
    speed: int
    background_color: str
    width_treatment: WidthTreatment = WidthTreatment.SCALE
    height_treatment: HeightTreatment = HeightTreatment.SCALE
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER

    def __init__(
        self,
        filename: str,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        speed: int = DEFAULT_ANIMATION_SPEED,
        width_treatment: WidthTreatment = WidthTreatment.SCALE,
        height_treatment: HeightTreatment = HeightTreatment.SCALE,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
        vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    ) -> None:
        self.filename = filename
        self.speed = speed
        self.background_color = background_color
        self.width_treatment = width_treatment
        self.height_treatment = height_treatment
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        raw_data = create_animation_payload(
            self.filename,
            background_color=self.background_color,
            sign_width=self.get_device_width,
            sign_height=self.get_device_height,
            speed=self.speed,
            width_treatment=self.width_treatment,
            height_treatment=self.height_treatment,
            horizontal_alignment=self.horizontal_alignment,
            vertical_alignment=self.vertical_alignment,
        )
        return self.chop_up_data(raw_data, self.hardware.cmdbyte_animation())

    @staticmethod
    def expect_notify() -> bool:
        return True


class SetJT(Command):
    """Set the display image by loading from a JT file"""

    filename: str
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE
    background_color: str

    def __init__(
        self,
        filename: str,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
        height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
        vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    ) -> None:
        self.filename = filename
        self.background_color = background_color
        self.width_treatment = width_treatment
        self.height_treatment = height_treatment
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        # raw_data = create_image_payload(
        raw_data, render_as_image = create_JT_payload(
            self.filename,
            background_color=self.background_color,
            sign_width=self.get_device_width,
            sign_height=self.get_device_height,
            width_treatment=self.width_treatment,
            height_treatment=self.height_treatment,
            horizontal_alignment=self.horizontal_alignment,
            vertical_alignment=self.vertical_alignment,
        )
        return self.chop_up_data(
            raw_data,
            self.hardware.cmdbyte_image()
            if render_as_image
            else self.hardware.cmdbyte_animation(),
        )

    @staticmethod
    def expect_notify() -> bool:
        return True
