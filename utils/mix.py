#!/usr/bin/python3
"""
Create a colorful text message.

Color mix can be specified using rgbymcwk as 2nd argument.
"""

import subprocess  # nosec: B404
import sys

MIN_ARGS = 2

if len(sys.argv) < MIN_ARGS:
    print(
        "-------------------------------------------------------------------------------",
    )
    print(
        "Usage: "
        + sys.argv[0]
        + ' "Text Message" <rgbymcwk (optional color mix)> <optional args>',
    )
    print(
        "-------------------------------------------------------------------------------",
    )
    sys.exit()

colors = {
    "r": "<#FF0000>",
    "g": "<#00FF00>",
    "b": "<#0000FF>",
    "y": "<#FFFF00>",
    "m": "<#FF00FF>",
    "c": "<#00FFFF>",
    "w": "<#FFFFFF>",
    "k": "<#000000>",
}
cidx = "rgbymcw"
i = 0
cmd = '"'
text = sys.argv[1]
oidx = len(sys.argv)

MIN_ARGS_WITH_COLOR = 3

if len(sys.argv) > MIN_ARGS_WITH_COLOR - 1:
    j = True
    oidx = 2
    for color_char in sys.argv[2]:
        if "rgbymcwk".find(color_char) < 0:
            j = False
            break
    if j:
        cidx = sys.argv[2]
        oidx = MIN_ARGS_WITH_COLOR

for letter in text:
    if letter == " ":
        cmd += letter
    else:
        cmd += colors[cidx[i]] + letter
        i += 1
        if i > len(cidx) - 1:
            i = 0

cmd += '"'
cmd_args = ["./tweak_sign.py", "-t", cmd, *sys.argv[oidx:]]
print(" ".join(cmd_args))
subprocess.run(cmd_args, check=False)  # nosec: B603  # noqa: S603
