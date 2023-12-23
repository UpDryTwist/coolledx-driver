"""Simply utility to scan for CoolLEDX devices and print out information about them."""

import argparse
import asyncio
import logging

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.exc import BleakError

# These just make it easier during dev, to not have to pass in command line arguments
FORCE_PRINT_ALL_ITEMS = False
FORCE_EXTENDED_INFO = False

DEFAULT_LOGGING = "WARNING"
DEFAULT_TIMEOUT = 10.0  # seconds

COOLLEDX_DEVICE_NAME = "CoolLEDX"

LOGGER = logging.getLogger(__name__)


async def detection_callback(
    device: BLEDevice, advertisement_data: AdvertisementData
) -> None:
    """Callback for when a device is detected"""
    LOGGER.debug(f"Device detected: {device} {advertisement_data}")


async def print_device_info(
    device: BLEDevice,
    advertisement: AdvertisementData,
    include_service_info: bool = True,
) -> None:
    """Print information about a device"""

    print(advertisement)
    if include_service_info:
        await print_service_info(device)


async def print_service_info(device: BLEDevice, timeout: float = 10.0) -> None:
    """Use a BleakClient to read out the service characteristics for a device"""

    async with BleakClient(device, timeout=timeout) as client:
        for service in client.services:
            print(f"[Service] {service}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(
                            f"  [Characteristic] {char} ({','.join( char.properties )})"
                            ", Value: {value}"
                        )
                    except Exception:
                        print(
                            f"  [Characteristic] {char} ({','.join( char.properties )})"
                            ", Error: {e}"
                        )
                else:
                    print(f"  [Characteristic] {char} ({','.join( char.properties )})")

                for descriptor in char.descriptors:
                    try:
                        value = await client.read_gatt_descriptor(descriptor.handle)
                        print(f"    [Descriptor] {descriptor}, Value: {value}")
                    except Exception as e:
                        print(f"    [Descriptor] {descriptor}, Error: {e}")


async def main():
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
        detection_callback=detection_callback, timeout=args.timeout, return_adv=True
    )

    for d, a in devices.values():
        try:
            is_coolledx = d.name == COOLLEDX_DEVICE_NAME
            if is_coolledx or args.all:
                print()
                print("-" * 80)
                print(f"Device: {d.name} ({d.address}), RSSI: {a.rssi}")
                if is_coolledx:
                    (key, value) = next(iter(a.manufacturer_data.items()))
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
                    await print_device_info(d, a)
        except BleakError as e:
            print(f"Connection received Bleak error: {e}")
        except Exception as e:
            print(f"Connection received unknown error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
