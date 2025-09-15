#!/usr/bin/python3
"""Send some commands to our sign . . ."""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import TYPE_CHECKING, NoReturn

from bleak.exc import BleakError

if TYPE_CHECKING:
    import argparse

from coolledx.argparser import parse_standard_arguments
from coolledx.client import Client
from coolledx.commands import (
    Initialize,
    InvertDisplay,
    InvertOrSomething,
    PowerDown,
    SendRawData,
    # SetMusicBars,  # <- add this
    # TurnOnOffButton,  # <- add this
    SetAnimation,
    SetBrightness,
    SetImage,
    SetJT,  # <- add this
    SetMode,
    SetSpeed,
    SetText,
    ShowChargingAnimation,
    StartupWithBatteryLevel,
    TurnOnOffApp,
)

LOGGER = logging.getLogger(__name__)


def handle_connection_error(
    error: TimeoutError | BleakError | asyncio.CancelledError,
    device_address: str | None,
) -> NoReturn:
    """Handle connection errors with helpful error messages and exit."""
    if isinstance(error, TimeoutError):
        LOGGER.error("Connection timed out while trying to connect to the LED sign")
        if device_address:
            print(
                f"Error: Connection timed out while connecting to device {device_address}",
            )
            print("Suggestions:")
            print("  - Ensure the LED sign is powered on and in range")
            print("  - Check that the MAC address is correct")
            print("  - Try moving closer to the device")
            print("  - Ensure no other devices are connected to the sign")
        else:
            print("Error: Connection timed out while scanning for LED signs")
            print("Suggestions:")
            print("  - Ensure the LED sign is powered on and in range")
            print("  - Try specifying the device MAC address with -a option")
            print("  - Check that the device name is correct (use -d option)")
    elif isinstance(error, BleakError):
        LOGGER.error("Bluetooth error occurred: %s", error)
        print(f"Error: Bluetooth communication failed - {error}")
        print("Suggestions:")
        print("  - Check that Bluetooth is enabled on your system")
        print("  - Ensure the LED sign is not connected to another device")
        print("  - Try restarting the LED sign")
        print("  - Check system Bluetooth permissions")
    elif isinstance(error, asyncio.CancelledError):
        LOGGER.error("Connection was cancelled")
        print("Error: Connection was cancelled or interrupted")
        print("Suggestions:")
        print("  - Try running the command again")
        print("  - Ensure stable Bluetooth connection")
    else:
        LOGGER.error("Unexpected error occurred: %s", error)
        print(f"Error: Unexpected error occurred - {error}")
        print("Run with --log DEBUG for more detailed information")

    sys.exit(1)


async def send_funky_commands(client: Client, args: argparse.Namespace) -> None:
    """Send funky commands to the LED sign."""
    if not args.funky:
        return

    LOGGER.info("Sending funky command: %s", args.funky)
    if args.funky == "invert":
        await client.send_command(InvertDisplay(inverted=True))
    elif args.funky == "revert":
        await client.send_command(InvertDisplay(inverted=False))
    elif args.funky == "charging":
        await client.send_command(ShowChargingAnimation())
    elif args.funky == "startup":
        await client.send_command(StartupWithBatteryLevel(15))
    elif args.funky == "powerdown":
        await client.send_command(PowerDown())
    elif args.funky == "initialize":
        await client.send_command(Initialize())
    elif args.funky == "invertorsomething":
        await client.send_command(InvertOrSomething())
    else:
        print(f"Unknown funky command: {args.funky}")


async def send_content_commands(client: Client, args: argparse.Namespace) -> None:
    """Send content commands (text, image, animation, JT) to the LED sign."""
    if args.text:
        LOGGER.info("Sending text command: %s", args.text)
        await client.send_command(
            SetText(
                args.text,
                default_color=args.color,
                background_color=args.background_color,
                color_markers=(args.start_color_marker, args.end_color_marker),
                font=args.font,
                font_height=args.font_height,
                render_as_text=False,
                width_treatment=args.width_treatment,
                height_treatment=args.height_treatment,
                horizontal_alignment=args.horizontal_alignment,
                vertical_alignment=args.vertical_alignment,
            ),
        )
    if args.image:
        LOGGER.info("Sending image command: %s", args.image)
        await client.send_command(
            SetImage(
                args.image,
                background_color=args.background_color,
                width_treatment=args.width_treatment,
                height_treatment=args.height_treatment,
                horizontal_alignment=args.horizontal_alignment,
                vertical_alignment=args.vertical_alignment,
            ),
        )
    if args.animation:
        LOGGER.info("Sending animation command: %s", args.animation)
        await client.send_command(
            SetAnimation(
                args.animation,
                speed=args.animation_speed,
                background_color=args.background_color,
                width_treatment=args.width_treatment,
                height_treatment=args.height_treatment,
                horizontal_alignment=args.horizontal_alignment,
                vertical_alignment=args.vertical_alignment,
            ),
        )
    if args.jtfile:
        LOGGER.info("Sending JT file command: %s", args.jtfile)
        await client.send_command(
            SetJT(
                args.jtfile,
                background_color=args.background_color,
                width_treatment=args.width_treatment,
                height_treatment=args.height_treatment,
                horizontal_alignment=args.horizontal_alignment,
                vertical_alignment=args.vertical_alignment,
            ),
        )


async def send_setting_commands(client: Client, args: argparse.Namespace) -> None:
    """Send setting commands (speed, brightness, mode, on/off) to the LED sign."""
    if args.speed >= 0:
        LOGGER.info("Setting speed: %s", args.speed)
        await client.send_command(SetSpeed(args.speed))
    if args.brightness >= 0:
        LOGGER.info("Setting brightness: %s", args.brightness)
        await client.send_command(SetBrightness(args.brightness))
    if args.mode >= 0:
        LOGGER.info("Setting mode: %s", args.mode)
        await client.send_command(SetMode(args.mode))
    if args.onoff >= 0:
        LOGGER.info("Setting on/off: %s", args.onoff)
        await client.send_command(TurnOnOffApp(args.onoff))


async def main() -> None:
    """Send commands to the CoolLEDX sign."""
    args = parse_standard_arguments()

    # Configure logging with more detailed format for better debugging
    logging.basicConfig(
        level=args.log.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Create client with configurable timeout and retry settings
        client_config = {
            "address": args.address,
            "device_name": args.device_name,
            "connection_timeout": args.connection_timeout,
            "connection_retries": args.connection_retries,
        }
        LOGGER.info(
            "Connecting to LED sign with timeout=%.1fs, retries=%d",
            args.connection_timeout,
            args.connection_retries,
        )

        async with Client(**client_config) as client:
            LOGGER.info("Successfully connected to LED sign")

            if args.raw:
                LOGGER.info("Sending raw data command")
                await client.send_command(SendRawData(args.raw))

            await send_funky_commands(client, args)
            await send_content_commands(client, args)
            await send_setting_commands(client, args)

            LOGGER.info("All commands sent successfully")
            print("LED sign update completed successfully")

    except (TimeoutError, BleakError, asyncio.CancelledError) as e:
        handle_connection_error(e, args.address)
    except Exception as e:
        LOGGER.exception("Unexpected error occurred")
        print(f"Error: Failed to update LED sign - {e}")
        print("Run with --log DEBUG for more detailed information")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except (OSError, RuntimeError) as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
