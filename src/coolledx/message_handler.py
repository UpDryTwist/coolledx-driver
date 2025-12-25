"""Handle messages returned from the device."""

from __future__ import annotations

import abc

class MessageHandler(abc.ABC):
    """Abstract class for message handler."""

    @abc.abstractmethod
    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""


class CoolLEDXMessageHandler(MessageHandler):
    """Message handler for CoolLEDX devices."""

    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""
        print(f"Received message: {message}")   


class CoolLEDMMessageHandler(MessageHandler):
    """Message handler for CoolLEDM devices."""

    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""
        print(f"Received message: {message}")   


class CoolLEDUMessageHandler(MessageHandler):
    """Message handler for CoolLEDU devices."""

    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""
        print(f"Received message: {message}")   



class CoolLEDMXMessageHandler(MessageHandler):
    """Message handler for CoolLEDMX devices."""

    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""
        print(f"Received message: {message}")   


class CoolLEDUXMessageHandler(MessageHandler):
    """Message handler for CoolLEDUX devices."""

    def handle_message(self, message: bytearray) -> None:
        """Handle a message from the device."""
        print(f"Received message: {message}")   


