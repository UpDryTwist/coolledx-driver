"""Client class for sending commands to the CoolLEDX device."""
import asyncio
import logging
from typing import Optional

from bleak import (
    BleakClient,
    BleakScanner,
)
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from .commands import Command

COOLLEDX_DEVICE_NAME = "CoolLEDX"
# There is also some device with name "FS" that is picked up as a Glowaler device.
# You can find it referenced here:
# https://gitee.com/juntong-iOS/CROSBY_Combine/blob/master/CROSBY_Combine/Classess/Tools/BluetoothManager.
# I don't have one of these, so I don't know what it is; don't know how extensible
# this code would be to manage it.

SERVICE_1801_CHAR = "00002a05-0000-1000-8000-00805f9b34fb"
SERVICE_FFF0_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"

DEFAULT_CONNECTION_TIMEOUT = 10.0  # Max seconds to wait for a connection
DEFAULT_COMMAND_NOTIFY_TIMEOUT = 1.0  # Max seconds to wait for a command notify
DEFAULT_CONNECTION_RETRIES = (
    5  # Number of times to retry a connection before giving up.  4 seemed to work.
)
CONNECTION_RETRY_DELAY = 1.0  # Seconds to wait between connection retries

LOGGER = logging.getLogger(__name__)


class Client:
    """Client class for sending commands to the CoolLEDX device."""

    device_address: Optional[str] = None
    bleak_client: Optional[BleakClient] = None
    ble_device: Optional[BLEDevice] = None
    characteristic_uuid: str
    connection_timeout: float
    command_timeout: float
    connection_retries: int
    height: int
    width: int

    def __init__(
        self,
        address: Optional[str] = None,
        connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
        command_timeout: float = DEFAULT_COMMAND_NOTIFY_TIMEOUT,
        connection_retries: int = DEFAULT_CONNECTION_RETRIES,
    ) -> None:
        """Set up the client.

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
        self.connection_timeout = connection_timeout
        self.command_timeout = command_timeout
        self.connection_retries = connection_retries
        self.characteristic_uuid = SERVICE_FFF0_CHAR

    # Support async context management

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self) -> None:
        """
        Connect to the device, by address if an address was supplied, otherwise by
        scanning for the first device. We'll retry the connection a few times if it
        fails; not sure exactly what causes this, but seems fairly easy to recover
        this way.
        """
        retries_remaining = self.connection_retries
        while retries_remaining > 0:
            try:
                retries_remaining -= 1
                if self.device_address is None:
                    ble_device = await BleakScanner.find_device_by_name(  # type: ignore
                        name=COOLLEDX_DEVICE_NAME,
                        timeout=self.connection_timeout,
                    )
                else:
                    ble_device = await BleakScanner.find_device_by_address(
                        # type: ignore
                        device_identifier=self.device_address,
                        timeout=self.connection_timeout,
                    )

                if ble_device is None:
                    raise BleakError(
                        "Unable to locate a CoolLEDX device when scanning."
                    )

                # In theory, we are supposed to now fetch
                # BleakScanner.discovered_devices_and_advertisement_data and iterate
                # through to re-find our device and the associated advertisement data.
                # Instead, just pull the metadata, as it's still supported.  Eat the
                # warning.
                # TODO:  Fix this to read the advertisement data during the scan, which
                #  will require rewriting the entire scanning process :(.
                manufacturer_data = ble_device.metadata["manufacturer_data"]
                (key, value) = next(iter(manufacturer_data.items()))
                # Manufacturer data:
                # [00 .. 05] = MAC address
                # [06] = height
                # [07] = 0?
                # [08] = width
                # [09] = 1?
                # [10] = 0?
                height = value[6]
                width = value[8]

                bleak_client = BleakClient(
                    ble_device,
                    timeout=self.connection_timeout,
                    disconnected_callback=self.handle_disconnect,
                    # services=[ SERVICE_FFF0_CHAR ]  >> filtering doesn't work!
                )
                await bleak_client.connect()
                # Wait to set these until we're sure it's a successful connection
                self.ble_device = ble_device
                self.bleak_client = bleak_client
                self.height = height
                self.width = width
                break
            except BleakError as e:
                LOGGER.warning(
                    f"Connection to CoolLEDX (address: {self.device_address} "
                    "received exception: {e}"
                )
                if retries_remaining <= 0:
                    LOGGER.error(
                        f"Connection failed after {self.connection_retries} "
                        "attempts."
                    )
                    raise e
                await asyncio.sleep(CONNECTION_RETRY_DELAY)
        if self.bleak_client is None:
            raise TypeError("bleak_client should not be None after connection.")
        await self.bleak_client.start_notify(
            self.characteristic_uuid, self.handle_notify
        )

    def handle_notify(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """
        The device called us back after we sent a command.  We listen here just for
        monitoring purposes at this point (an older version of the code used this to
        delay for the notification and manage an event).
        """
        if sender.uuid != self.characteristic_uuid:
            LOGGER.warning(
                "Received notification from unexpected characteristic: from "
                "{sender} data: {data.hex()}"
            )
        else:
            LOGGER.debug(f"Received notification: from {sender} data: {data.hex()}")

    @staticmethod
    def handle_disconnect(client: BleakClient) -> None:
        """We received a disconnect from the BLE implementation."""
        LOGGER.info(f"Disconnected from device: {client}")
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
        chunks = command.get_command_chunks()
        for chunk in chunks:
            LOGGER.debug(f"Sending chunk: {chunk.hex()}")
            await self.write_raw(chunk, command.expect_notify())

    async def write_raw(self, data: bytearray, expect_response: bool = False) -> None:
        if self.bleak_client is None:
            raise TypeError("bleak_client should not be None after connection.")
        await self.bleak_client.write_gatt_char(
            self.characteristic_uuid, data, response=expect_response
        )

    async def write_hexstr(self, data: str, expect_response: bool = False) -> None:
        await self.write_raw(bytearray.fromhex(data), expect_response)

    async def disconnect(self) -> None:
        if self.bleak_client is not None:
            await self.bleak_client.stop_notify(self.characteristic_uuid)
