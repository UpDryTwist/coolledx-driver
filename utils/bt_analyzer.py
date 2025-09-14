"""
For analyzing the Bluetooth logs from a phone to try to crack the packet protocol.

In general:
- Turn on Bluetooth logging on the phone (under developer options)
- Run CoolLED1248 application to generate the traffic you want to see
- Get the logs from the phone with "adb bugreport [myfile]", and then find the
  logs in the ZIP file under FS/data/misc/bluetooth/logs/btsnoop_hci.log
- Then run this script to strip down to the API handshake
"""

import argparse

import pyshark

from coolledx.decoder import CoolCommand


def main() -> None:
    """Analyze Bluetooth logs to crack the packet protocol."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Wireshark style packet capture file to analyze",
    )
    parser.add_argument(
        "-a",
        "--address",
        help="MAC address of the sign",
    )
    parser.add_argument(
        "-n",
        "--handle",
        help="Handle to filter on",
        default="0x59",
    )
    parser.add_argument(
        "-u",
        "--uuid",
        help="UUID to filter on",
        default="0x2aa6",
    )
    parser.add_argument(
        "-i",
        "--ignoreunknownpackets",
        help="Ignore packets that don't match the expected format",
        default=True,
    )
    parser.add_argument(
        "-t",
        "--tsharkpath",
        help="Path to tshark executable",
        default=None,
    )
    args = parser.parse_args()

    # f" and btatt.handle == {args.handle}"
    bt_filter = (
        f"( bthci_acl.dst.bd_addr == {args.address} or bthci_acl.src.bd_addr == {args.address} ) "
        f" and ( btatt.characteristic_uuid16 == {args.uuid} or btatt.service_uuid16 == 0xfff0 or btatt.service_uuid16 == 0xfff1)"
    )
    print(f"Filtering {args.file} on {bt_filter}")

    cap = pyshark.FileCapture(
        args.file,
        display_filter=bt_filter,
        tshark_path=args.tsharkpath,
    )

    commands = []

    for pkt in cap:
        if "btatt" not in pkt or not hasattr(pkt.btatt, "value"):
            if not args.ignoreunknownpackets:
                print("** Unexpected packet contents **")
                print(pkt)
            continue
        # print(f"{pkt.btatt.value}")
        cmd = CoolCommand(
            pkt.bthci_acl.dst_bd_addr == args.address,
            pkt.bthci_acl.src_name,
            pkt.bthci_acl.dst_name,
            pkt.btatt.handle,
            bytearray(pkt.btatt.value.binary_value),
        )
        commands.append(cmd)

    for cmd in commands:
        print(cmd)


if __name__ == "__main__":
    main()
