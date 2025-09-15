"""Client class for sending commands to the CoolLEDX device."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Self

from bleak import (
    BleakClient,
    BleakScanner,
)
from bleak.exc import BleakError

if TYPE_CHECKING:
    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice

from .commands import Command, CommandStatus, CoolLedError, ErrorCode
from .decoder import CoolCommand
from .hardware import CoolLED

# There is also some device with name "FS" that is picked up as a Glowaler device.
# You can find it referenced here:
# https://gitee.com/juntong-iOS/CROSBY_Combine/blob/master/CROSBY_Combine/Classess/Tools/BluetoothManager.
# I don't have one of these, so I don't know what it is; don't know how extensible
# this code would be to manage it.
# 2024-11-23:  Added CoolLEDM to the list of supported names, per fr-og.  I don't have
#              one, so this is more to make it easier for someone else to use this,
#              but can't prove it works . . .

SERVICE_1801_CHAR = "00002a05-0000-1000-8000-00805f9b34fb"
SERVICE_FFF0_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"

DEFAULT_CONNECTION_TIMEOUT = 10.0  # Max seconds to wait for a connection
DEFAULT_COMMAND_NOTIFY_TIMEOUT = 1.0  # Max seconds to wait for a command notify
DEFAULT_CONNECTION_RETRIES = (
    5  # Number of times to retry a connection before giving up.  4 seemed to work.
)
CONNECTION_RETRY_DELAY = 1.0  # Seconds to wait between connection retries
DEFAULT_DEVICE_NAME = "CoolLEDX"
MIN_MANUFACTURER_DATA_LENGTH = 9  # Minimum length to contain height and width data

LOGGER = logging.getLogger(__name__)


class Client:
    """Client class for sending commands to the CoolLEDX device."""

    device_address: str | None = None
    bleak_client: BleakClient | None = None
    ble_device: BLEDevice | None = None
    characteristic_uuid: str
    connection_timeout: float
    command_timeout: float
    connection_retries: int
    height: int
    width: int
    current_command: Command | None = None
    hardware: CoolLED = CoolLED()

    def __init__(
        self,
        address: str | None = None,
        device_name: str | None = DEFAULT_DEVICE_NAME,
        connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
        command_timeout: float = DEFAULT_COMMAND_NOTIFY_TIMEOUT,
        connection_retries: int = DEFAULT_CONNECTION_RETRIES,
    ) -> None:
        """
        Set up the client.

        If address is None, then we will scan to find the first CoolLEDX device
        (nondeterministic if multiple devices are present).  So if you only have one
        CoolLEDX device (within bluetooth range), then you don't need to
        supply an address.  If you have multiple devices, you should supply an address.

        The connection timeout is the timeout used during the connection process (both
        for the scan, and for the connection itself).  The command timeout is the
        timeout used when waiting for a notification from the device after sending a
        command.

        Connection retries is the number of full reattempts to make.  In my experience,
        sometimes you'll not find the sign advertising, sometimes you'll get another
        error.  I was always able to connect within 4 retries, but we default to 5 for
        safety.  This DOES mean that it'll spin for a while if there's no sign around.
        """
        self.device_address = address
        self.device_name = device_name
        self.connection_timeout = connection_timeout
        self.command_timeout = command_timeout
        self.connection_retries = connection_retries
        self.characteristic_uuid = SERVICE_FFF0_CHAR

    # Support async context management

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        """Exit async context manager."""
        await self.disconnect()

    async def connect(self) -> None:
        """
        Connect to the device, by address if an address was supplied, otherwise by
        scanning for the first device. We'll retry the connection a few times if it
        fails; not sure exactly what causes this, but seems fairly easy to recover
        this way.
        """
        LOGGER.debug("Initiating a connection to the device: %s", self.device_address)
        retries_remaining = self.connection_retries
        while retries_remaining > 0:
            try:
                retries_remaining -= 1
                ble_device, height, width = await self._discover_device()

                if ble_device is None:
                    LOGGER.debug("Unable to locate a CoolLEDX/M device when scanning.")
                    raise BleakError(
                        "Unable to locate a CoolLEDX/M device when scanning.",
                    )

                bleak_client = BleakClient(
                    ble_device,
                    timeout=self.connection_timeout,
                    disconnected_callback=self.handle_disconnect,
                    # services=[ SERVICE_FFF0_CHAR ]  >> filtering doesn't work!
                )
                LOGGER.debug("Connecting to device: %s", ble_device)
                await bleak_client.connect()
                LOGGER.debug("Connected to device: %s", ble_device)
                # Wait to set these until we're sure it's a successful connection
                self.ble_device = ble_device
                self.bleak_client = bleak_client
                self.height = height
                self.width = width
                break
            except (BleakError, TimeoutError, asyncio.CancelledError) as e:
                LOGGER.warning(
                    "Connection to CoolLEDX (address: %s) received exception: %s",
                    self.device_address,
                    e,
                )
                if retries_remaining <= 0:
                    LOGGER.exception(
                        "Connection failed after %s attempts.",
                        self.connection_retries,
                    )
                    raise
                LOGGER.info(
                    "Retrying connection in %s seconds (%s attempts remaining)...",
                    CONNECTION_RETRY_DELAY,
                    retries_remaining,
                )
                await asyncio.sleep(CONNECTION_RETRY_DELAY)
        if self.bleak_client is None:
            raise TypeError("bleak_client should not be None after connection.")
        await self.bleak_client.start_notify(
            self.characteristic_uuid,
            self.handle_notify,
        )

    async def _discover_device(self) -> tuple[BLEDevice | None, int, int]:
        """
        Discover a CoolLEDX/M device and extract height/width from advertisement data.

        Returns a tuple of (device, height, width) or (None, 0, 0) if not found.
        """
        LOGGER.debug("Scanning for devices...")

        # Use the new Bleak API to discover devices with advertisement data
        devices = await BleakScanner.discover(
            timeout=self.connection_timeout,
            return_adv=True,
        )

        target_device_name = (
            self.device_name if self.device_name else DEFAULT_DEVICE_NAME
        )

        for device, advertisement_data in devices.values():
            # Check if this is the device we're looking for
            if self.device_address is not None:
                # Looking for specific address
                if device.address.lower() != self.device_address.lower():
                    continue
            elif device.name != target_device_name:
                # Looking for specific device name
                continue

            LOGGER.debug("Found target device: %s (%s)", device.name, device.address)

            # Extract height and width from manufacturer data
            if not advertisement_data.manufacturer_data:
                LOGGER.warning("Device %s has no manufacturer data", device.address)
                continue

            try:
                # Get the first (and typically only) manufacturer data entry
                # We don't need the manufacturer ID, just the data
                value = next(iter(advertisement_data.manufacturer_data.values()))

                # Manufacturer data format:
                # [00 .. 05] = MAC address
                # [06] = height
                # [07] = 0?
                # [08] = width
                # [09] = 1?
                # [10] = 0?
                if len(value) < MIN_MANUFACTURER_DATA_LENGTH:
                    LOGGER.warning(
                        "Device %s manufacturer data too short: %s",
                        device.address,
                        value.hex(),
                    )
                    continue

                height = value[6]
                width = value[8]

                LOGGER.debug(
                    "Device %s dimensions: %dx%d",
                    device.address,
                    width,
                    height,
                )

            except (IndexError, StopIteration) as e:
                LOGGER.warning(
                    "Failed to parse manufacturer data for device %s: %s",
                    device.address,
                    e,
                )
                continue
            else:
                return device, height, width

        # Device not found
        LOGGER.debug("Target device not found in scan results")
        return None, 0, 0

    def handle_notify(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """
        Handle device notification callback.

        The device called us back after we sent a command. We listen here just for
        monitoring purposes at this point (an older version of the code used this to
        delay for the notification and manage an event).
        """
        if sender.uuid != self.characteristic_uuid:
            LOGGER.warning(
                "Received notification from unexpected characteristic: from %s data: %s",
                sender,
                data.hex(),
            )
        else:
            LOGGER.debug("Received notification: from %s data: %s", sender, data.hex())
            cmd = CoolCommand(False, "Sign", "Us", sender.handle, data)  # noqa: FBT003
            LOGGER.debug("Received notification (decoded): %s", cmd)
            if self.current_command:
                # TODO:  This isn't entirely accurate.  I just don't know how to
                #        properly interpret the errors from the devices yet.
                self.current_command.set_command_status(CommandStatus.ACKNOWLEDGED)
                self.current_command.error_code = ErrorCode.SUCCESS
                if self.current_command.future:
                    self.current_command.future.set_result(0)
            else:
                LOGGER.error("Received a notification without a current command.")

    @staticmethod
    def handle_disconnect(client: BleakClient) -> None:
        """Handle BLE disconnect callback."""
        LOGGER.info("Disconnected from device: %s", client)
        # We don't need to actually do anything, as we'll pick up the disconnected
        # state and reconnect if we need to when we issue our next command.

    async def force_connected(self) -> None:
        """Force a connection to the device."""
        if self.bleak_client is None or not self.bleak_client.is_connected:
            await self.connect()

    async def send_command(self, command: Command) -> None:
        """Send a command to the device; wait for response if needed."""
        await self.force_connected()
        command.set_dimensions(height=self.height, width=self.width)
        command.set_hardware(self.hardware)
        chunks = command.get_command_chunks()
        try:
            for chunk in chunks:
                LOGGER.debug("Sending chunk: %s", chunk.hex())
                cmd = CoolCommand(True, "Us", "Sign", 0x00, chunk)  # noqa: FBT003
                LOGGER.debug("Sending command: %s", cmd)
                self.current_command = command
                command.command_status = CommandStatus.TRANSMITTED
                command.set_future(asyncio.get_event_loop().create_future())
                await self.write_raw(chunk, expect_response=command.expect_notify())
                if command.expect_notify() and command.future:
                    await asyncio.wait_for(command.future, timeout=self.command_timeout)
                    if command.command_status == CommandStatus.TRANSMITTED:
                        LOGGER.error(
                            "Command %s did not receive a notification within %s seconds.",
                            command,
                            self.command_timeout,
                        )
                        break
                    if command.command_status == CommandStatus.ERROR:
                        error_name = ErrorCode.get_error_code_name(command.error_code)
                        LOGGER.error(
                            "Command %s received an error response: %s(%s)",
                            command,
                            error_name,
                            command.error_code,
                        )
                        raise CoolLedError(
                            f"Command {command} received an error response: {error_name}({command.error_code})",
                        )

        except Exception:
            LOGGER.exception("Error sending command: %s", command)
            self.current_command = None
            raise

    async def write_raw(
        self,
        data: bytearray,
        *,
        expect_response: bool = False,
    ) -> None:
        """Write raw data to the device characteristic."""
        if self.bleak_client is None:
            raise TypeError("bleak_client should not be None after connection.")
        await self.bleak_client.write_gatt_char(
            self.characteristic_uuid,
            data,
            response=expect_response,
        )

    async def write_hexstr(self, data: str, *, expect_response: bool = False) -> None:
        """Write hex string data to the device characteristic."""
        await self.write_raw(bytearray.fromhex(data), expect_response=expect_response)

    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        if self.bleak_client is not None:
            LOGGER.debug("Disconnecting from device: %s", self.bleak_client)
            await self.bleak_client.stop_notify(self.characteristic_uuid)
