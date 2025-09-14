"""Simply utility to scan for CoolLEDX devices and print out information about them."""

import argparse
import asyncio
import logging
from typing import Any

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.exc import BleakError

# These just make it easier during dev, to not have to pass in command line arguments
FORCE_PRINT_ALL_ITEMS = False
FORCE_EXTENDED_INFO = False

DEFAULT_LOGGING = "WARNING"
DEFAULT_TIMEOUT = 10.0  # seconds

COOLLEDX_DEVICE_NAMES = [
    "CoolLEDX",
    "CoolLEDM",
]  # There is also some device with name "FS" that is picked up as a Glowaler device.

LOGGER = logging.getLogger(__name__)


async def _print_descriptor_info(client: BleakClient, descriptor: Any) -> None:
    """Print information about a descriptor."""
    try:
        value = await client.read_gatt_descriptor(descriptor.handle)
        print(f"    [Descriptor] {descriptor}, Value: {value}")
    except BleakError as e:
        print(f"    [Descriptor] {descriptor}, Error: {e}")


async def _process_device(
    device: BLEDevice,
    advertisement: AdvertisementData,
    args: Any,
) -> None:
    """Process a single device."""
    is_coolledx = device.name in COOLLEDX_DEVICE_NAMES
    if is_coolledx or args.all:
        print()
        print("-" * 80)
        print(f"Device: {device.name} ({device.address}), RSSI: {advertisement.rssi}")
        if is_coolledx:
            (_key, value) = next(iter(advertisement.manufacturer_data.items()))
            # Manufacturer data:
            # [00 .. 05] = MAC address
            # [06] = height
            # [07] = 0?
            # [08] = width
            # [09] = 1?
            # [10] = 0?
            height = value[6]
            width = value[8]
            print(f"  Height: {height}, Width: {width}")

        if args.extended:
            await print_device_info(device, advertisement)


async def _process_all_devices(devices: Any, args: Any) -> None:
    """Process all discovered devices."""
    for d, a in devices.values():
        try:
            await _process_device(d, a, args)
        except BleakError as e:
            print(f"Connection received Bleak error: {e}")


async def detection_callback(
    device: BLEDevice,
    advertisement_data: AdvertisementData,
) -> None:
    """Handle device detection callback."""
    LOGGER.debug("Device detected: %s %s", device, advertisement_data)


async def print_device_info(
    device: BLEDevice,
    advertisement: AdvertisementData,
    *,
    include_service_info: bool = True,
) -> None:
    """Print information about a device."""
    print(advertisement)
    if include_service_info:
        await print_service_info(device)


async def print_service_info(device: BLEDevice, timeout: float = 10.0) -> None:
    """Use a BleakClient to read out the service characteristics for a device."""
    async with BleakClient(device, timeout=timeout) as client:
        for service in client.services:
            print(f"[Service] {service}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(
                            f"  [Characteristic] {char} ({','.join(char.properties)})"
                            ", Value: {value}",
                        )
                    except BleakError as e:
                        print(
                            f"  [Characteristic] {char} ({','.join(char.properties)})"
                            f", Error: {e}",
                        )
                else:
                    print(f"  [Characteristic] {char} ({','.join(char.properties)})")

                for descriptor in char.descriptors:
                    await _print_descriptor_info(client, descriptor)


async def main() -> None:
    """Scan bluetooth devices and print out what we find."""
    parser = argparse.ArgumentParser(description="Bluetooth scanning arguments.")
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Dump all devices, not just CoolLEDX devices",
        default=FORCE_PRINT_ALL_ITEMS,
    )
    parser.add_argument(
        "-e",
        "--extended",
        action="store_true",
        help="Dump extended information about devices",
        default=FORCE_EXTENDED_INFO,
    )
    parser.add_argument("-l", "--log", default=DEFAULT_LOGGING, help="Logging level")
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Timeout for scanning",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.log.upper())

    print(f"Scanning for {args.timeout} seconds (change duration with -t) . . .")
    print()

    devices = await BleakScanner.discover(
        timeout=args.timeout,
        return_adv=True,
    )

    await _process_all_devices(devices, args)


if __name__ == "__main__":
    asyncio.run(main())
