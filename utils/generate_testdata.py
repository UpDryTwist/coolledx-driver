"""
Generate test data for the tests.

Use this to generate data for the tests.
OK, this is a bit self-referential . . .
Obviously, only do this when you know that your code is good, so that the test
data is good!

For example:
python3 tests/generate_testdata.py --text "Hello, <#00ff00>world!" --color "#FF0000" --font arial --font-height 13   # noqa: E501
python3 tests/generate_testdata.py --image test-image.png --height-treatment crop-pad --horizontal-alignment center --vertical-alignment bottom   # noqa: E501
python3 tests/generate_testdata.py --animation test-animation.gif --horizontal-alignment left   # noqa: E501
"""

import sys

from coolledx.argparser import parse_standard_arguments
from coolledx.commands import SetAnimation, SetImage, SetText

args = parse_standard_arguments()

command = None
if args.text:
    command = SetText(
        args.text,
        default_color=args.color,
        color_markers=(args.start_color_marker, args.end_color_marker),
        font=args.font,
        font_height=args.font_height,
        render_as_text=True,
        width_treatment=args.width_treatment,
        height_treatment=args.height_treatment,
        horizontal_alignment=args.horizontal_alignment,
        vertical_alignment=args.vertical_alignment,
    )

elif args.image:
    command = SetImage(
        args.image,
        width_treatment=args.width_treatment,
        height_treatment=args.height_treatment,
        horizontal_alignment=args.horizontal_alignment,
        vertical_alignment=args.vertical_alignment,
    )
elif args.animation:
    command = SetAnimation(
        args.animation,
        width_treatment=args.width_treatment,
        height_treatment=args.height_treatment,
        horizontal_alignment=args.horizontal_alignment,
        vertical_alignment=args.vertical_alignment,
    )

if command is None:
    print("You must set either --text, --image, or --animation")
    sys.exit(1)

chunks = command.get_command_chunks()
for chunk in chunks:
    # Split into groups that'll fit into a PEP8 line
    max_length = 70
    hex_chunk = chunk.hex()
    lines = [
        hex_chunk[i : i + max_length] for i in range(0, len(hex_chunk), max_length)
    ]
    for line in lines:
        print(f'    "{line}"')
    print("    ,")
