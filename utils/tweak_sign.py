#!/usr/bin/python3
"""Send some commands to our sign . . ."""

import asyncio
import logging

from coolledx.argparser import parse_standard_arguments
from coolledx.client import Client
from coolledx.commands import (
    SetAnimation,
    SetBrightness,
    SetImage,
    SetJT,  # <- add this
    SetMode,
    SetSpeed,
    SetText,
    TurnOnOffApp,
)


async def main():
    args = parse_standard_arguments()

    logging.basicConfig(level=args.log.upper())

    async with Client(args.address) as client:
        if args.text:
            await client.send_command(
                SetText(
                    args.text,
                    default_color=args.color,
                    background_color=args.background_color,
                    color_markers=(args.start_color_marker, args.end_color_marker),
                    font=args.font,
                    font_height=args.font_height,
                    render_as_text=True,
                    width_treatment=args.width_treatment,
                    height_treatment=args.height_treatment,
                    horizontal_alignment=args.horizontal_alignment,
                    vertical_alignment=args.vertical_alignment,
                )
            )
        if args.image:
            await client.send_command(
                SetImage(
                    args.image,
                    background_color=args.background_color,
                    width_treatment=args.width_treatment,
                    height_treatment=args.height_treatment,
                    horizontal_alignment=args.horizontal_alignment,
                    vertical_alignment=args.vertical_alignment,
                )
            )
        if args.animation:
            await client.send_command(
                SetAnimation(
                    args.animation,
                    speed=args.animation_speed,
                    background_color=args.background_color,
                    width_treatment=args.width_treatment,
                    height_treatment=args.height_treatment,
                    horizontal_alignment=args.horizontal_alignment,
                    vertical_alignment=args.vertical_alignment,
                )
            )
        if args.jtfile:
            await client.send_command(
                SetJT(
                    args.jtfile,
                    background_color=args.background_color,
                    width_treatment=args.width_treatment,
                    height_treatment=args.height_treatment,
                    horizontal_alignment=args.horizontal_alignment,
                    vertical_alignment=args.vertical_alignment,
                )
            )
        if args.speed:
            await client.send_command(SetSpeed(args.speed))
        if args.brightness:
            await client.send_command(SetBrightness(args.brightness))
        await client.send_command(SetMode(args.mode))
        # This isn't working right now . . .
        # await client.send_command(
        #    SetMusicBars( bytearray(
        #                  [0x0f, 0x02, 0x04, 0x08, 0x0a, 0x0c, 0x0e, 0x0f] ),
        #                  bytearray(
        #                  [0x01, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07 ] ) ) )
        await client.send_command(TurnOnOffApp(args.onoff))
        # Not entirely sure what this does; not working right now.
        # await client.send_command( TurnOnOffButton( True ) )


if __name__ == "__main__":
    asyncio.run(main())
