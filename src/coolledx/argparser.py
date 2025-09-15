"""
Common set of arguments for the commands.  Used in the utils, and in the test
generator, so factored out.
"""

import argparse

from coolledx import (
    DEFAULT_ANIMATION_SPEED,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_COLOR,
    DEFAULT_END_COLOR_MARKER,
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_FUNKY,
    DEFAULT_HEIGHT_TREATMENT,
    DEFAULT_HORIZONTAL_ALIGNMENT,
    DEFAULT_LOGGING,
    DEFAULT_MODE,
    DEFAULT_ON_OFF,
    DEFAULT_START_COLOR_MARKER,
    DEFAULT_VERTICAL_ALIGNMENT,
    DEFAULT_WIDTH_TREATMENT,
)

DEFAULT_ADDRESS = None
DEFAULT_TEXT_TO_SEND = None
DEFAULT_SPEED = -1
DEFAULT_BRIGHTNESS = -1
DEFAULT_ANIMATION = None
DEFAULT_IMAGE = None
DEFAULT_JT = None
DEFAULT_DEVICE_NAME = "CoolLEDX"
DEFAULT_CONNECTION_TIMEOUT = 10.0
DEFAULT_CONNECTION_RETRIES = 5


def auto_int(x: str) -> int:
    """Convert a string to an int, with support for hex and octal strings."""
    return int(x, 0)


def parse_standard_arguments() -> argparse.Namespace:
    """Parse standard command line arguments for the CoolLEDX driver."""
    parser = argparse.ArgumentParser(description="Commands to send to the sign.")
    parser.add_argument(
        "-a",
        "--address",
        help="MAC address of the sign",
        default=DEFAULT_ADDRESS,
        nargs="?",
    )
    parser.add_argument(
        "-d",
        "--device-name",
        help="Name of the device to connect to; defaults to CoolLEDX",
        default=DEFAULT_DEVICE_NAME,
        nargs="?",
    )
    parser.add_argument(
        "-t",
        "--text",
        help="Text to display",
        default=DEFAULT_TEXT_TO_SEND,
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=auto_int,
        default=DEFAULT_SPEED,
        help="Speed of the scroller",
    )
    parser.add_argument(
        "-b",
        "--brightness",
        type=auto_int,
        default=DEFAULT_BRIGHTNESS,
        help="Brightness of the scroller",
    )
    parser.add_argument(
        "-c",
        "--color",
        default=DEFAULT_COLOR,
        help="Color of the text as #rrggbb hex or a color name",
    )
    parser.add_argument(
        "-C",
        "--background-color",
        default=DEFAULT_BACKGROUND_COLOR,
        help="Background color of the image as #rrggbb hex or a color name",
    )
    parser.add_argument(
        "-j",
        "--start-color-marker",
        default=DEFAULT_START_COLOR_MARKER,
        help="The open bracket used to indicate an #rrggbb hex color in the text",
    )
    parser.add_argument(
        "-k",
        "--end-color-marker",
        default=DEFAULT_END_COLOR_MARKER,
        help="The close bracket used to indicate an #rrggbb hex color in the text",
    )
    parser.add_argument("-f", "--font", default=DEFAULT_FONT, help="Font of the text")
    parser.add_argument(
        "-H",
        "--font-height",
        type=int,
        default=DEFAULT_FONT_SIZE,
        help="Font height of the text",
    )
    parser.add_argument("-l", "--log", default=DEFAULT_LOGGING, help="Logging level")
    parser.add_argument(
        "--connection-timeout",
        type=float,
        default=DEFAULT_CONNECTION_TIMEOUT,
        help="Timeout in seconds for Bluetooth connection attempts (default: 10.0)",
    )
    parser.add_argument(
        "--connection-retries",
        type=int,
        default=DEFAULT_CONNECTION_RETRIES,
        help="Number of connection retry attempts (default: 5)",
    )
    parser.add_argument(
        "-o",
        "--onoff",
        type=int,
        default=DEFAULT_ON_OFF,
        help="Turn on/off the scroller: 1=on, 0=off, -1=don't touch",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=int,
        default=DEFAULT_MODE,
        help="Mode of the scroller (1-8), or -1 to not touch",
    )
    parser.add_argument(
        "-i",
        "--image",
        default=DEFAULT_IMAGE,
        help="Image file to display",
    )
    parser.add_argument(
        "-n",
        "--animation",
        default=DEFAULT_ANIMATION,
        help="Animation file to display",
    )
    parser.add_argument(
        "-N",
        "--animation-speed",
        type=int,
        default=DEFAULT_ANIMATION_SPEED,
        help="Animation speed",
    )
    parser.add_argument(
        "-w",
        "--width-treatment",
        type=str,
        default=DEFAULT_WIDTH_TREATMENT,
        help="Width treatment (scale/crop-pad/as-is)",
    )
    parser.add_argument(
        "-g",
        "--height-treatment",
        type=str,
        default=DEFAULT_HEIGHT_TREATMENT,
        help="Height treatment (scale/crop-pad)",
    )
    parser.add_argument(
        "-z",
        "--horizontal-alignment",
        type=str,
        default=DEFAULT_HORIZONTAL_ALIGNMENT,
        help="Horizontal alignment (left/center/right/none)",
    )
    parser.add_argument(
        "-y",
        "--vertical-alignment",
        type=str,
        default=DEFAULT_VERTICAL_ALIGNMENT,
        help="Vertical alignment (top/center/bottom)",
    )
    parser.add_argument(
        "-jt",
        "--jtfile",
        default=DEFAULT_JT,
        help="JT file to display",
    )
    parser.add_argument(
        "-u",
        "--funky",
        type=str,
        default=DEFAULT_FUNKY,
        help="Send one of the funky commands: 'initialize', 'invert', 'revert', 'startup', 'powerdown', 'animation', 'invertorsomething'",
    )

    parser.add_argument(
        "-r",
        "--raw",
        type=str,
        default=None,
        help="Send a raw command to the sign.  Provide as a hex string, e.g. '01 02 03'",
    )
    return parser.parse_args()
