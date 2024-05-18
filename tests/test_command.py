"""Tests for Command"""

import inspect
import os

# pylint: disable=line-too-long
import platform
from typing import List

import pytest

from coolledx.commands import Command, SetAnimation, SetImage, SetSpeed, SetText
from coolledx.render import HeightTreatment, HorizontalAlignment, VerticalAlignment


def file_path_in_test_dir(file_name: str) -> str:
    """Return the path to a file in the tests directory"""
    tests_path = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))  # type: ignore
    )

    return f"{tests_path}/{file_name}"


def test_escape_bytes():
    assert Command.escape_bytes(
        bytearray(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f")
    ) == bytearray(
        b"\x00\x02\x05\x02\x06\x02\x07\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
        # noqa: E501
    )


def test_set_speed():
    """Test the SetSpeed command"""
    command = SetSpeed(0x01)
    assert command.get_command_hexstr(False) == "0100020607020503"
    command = SetSpeed(0x00)
    assert command.get_command_hexstr(False) == "01000206070003"
    command = SetSpeed(0xFF)
    assert command.get_command_hexstr(False) == "0100020607ff03"
    with pytest.raises(ValueError):
        SetSpeed(-1)
    with pytest.raises(ValueError):
        SetSpeed(256)


def confirm_chunks(chunks: List[bytearray], correct_values: List[str]):
    assert len(chunks) == len(correct_values)
    for i in range(len(chunks)):
        assert chunks[i].hex() == correct_values[i]


def test_set_text():
    """
    The appropriate generate_testdata.py command for this is:
    python3 tests/generate_testdata.py --text "Hello, <#00ff00>world!" --color "#FF0000" --font arial --font-height 13  # noqa: E501
    """

    # This test will only run on Windows 11, probably, as it relies on specific
    # font rendering.
    if platform.system() != "Windows" or platform.release() != "11":
        return

    correct_values = [
        "0100880206000206150000800000000000000000000000000000000000000000000000"
        "0016303030303030303030303030303030303030303030300000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000205aa00000ffc0ffc00800080008000800ffc0ffc00f8"
        "0205d303",
        "01008802060002061500020580fc0205ac0205ac0205ac0205ec00ec0ffc0ffc00000f"
        "fc0ffc000000f80205fc02058c02058c02058c0205fc00f80000000600060000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "000000000000000000004b03",
        "0100880206000206150002068000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "000000000000000000000205e00205fc003c0205fc0205f00205fc003c0205fc0205f0"
        "0205f80205fc02058c02058c02058c0205fc00f80205fc0205fc0205c00205800ffc0f"
        "fc000000f80205fc02058c02058c0205dc0ffc0ffc006003",
        "01008802060002061500020780000ff40ff40000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "009403",
        "01001d0206000206150004150000000000000000000000000000000000000000000603",
    ]

    confirm_chunks(
        SetText(
            "Hello, <#00ff00>world!",
            default_color="#FF0000",
            font="arial",
            font_height=13,
        ).get_command_chunks(),
        correct_values,
    )


def test_set_image():
    """
    The appropriate generate_testdata.py command for this is:
    python3 tests/generate_testdata.py --image test-image.png --height-treatment crop-pad --horizontal-alignment center --vertical-alignment bottom  # noqa: E501
    """
    correct_values = [
        "01008802070002059a0000800000000000000000000000000000000000000000000000"
        "0002058000000207e01ff83018400c400c400640064002060000000000000000100610"
        "06118633c4226426243624322410640ee607c000001000300030006000200020006000"
        "600060002000300818080c180ff008e01800180010001000100009c00dc00cc0000000"
        "0000004c03",
        "01008802070002059a000205800000000000000207e00e301c1830103198339831f800"
        "e000000000000000000000000002050007c00e4008301830181008100c100f300ff600"
        "0600060004000400040004000400040006000000001000300030006000200020006000"
        "600060002000300818080c180ff008e01800198011f81018100809c84dc86cc8600860"
        "083ffcdc03",
        "01008802070002059a000206801e00000000000207e00e301c1830103198339831f800"
        "e000000000000000000000000000000000000000000000000000000000000010061006"
        "118633c4226426243624322410640ee607d00018000c07cc04440ccc0ccc0c18020718"
        "0207f0000000000000000000000000000000000205800205f8001800080205c841c860"
        "c8600860083ffc9e03",
        "01002202070002059a0002071a1e00000000000207e00e301c1830103198339831f800"
        "e0000000004e03",
    ]

    confirm_chunks(
        SetImage(
            file_path_in_test_dir("test-image.png"),
            height_treatment=HeightTreatment.CROP_PAD,
            horizontal_alignment=HorizontalAlignment.CENTER,
            vertical_alignment=VerticalAlignment.BOTTOM,
        ).get_command_chunks(),
        correct_values,
    )


def test_set_animation():
    """
    The appropriate generate_testdata.py command for this is:
    python3 tests/generate_testdata.py --animation test-animation.gif --horizontal-alignment left # noqa: E501
    """
    correct_values = [
        "0100880400091b00008000000000000000000000000000000000000000000000000004"
        "0206000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000094"
        "03",
        "0100880400091b00020580000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000093"
        "03",
        "0100880400091b00020680000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000090"
        "03",
        "0100880400091b00020780000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000091"
        "03",
        "0100880400091b00048000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009603",
        "0100880400091b00058000000000000000000000000000000000000000000000000000"
        "000000000000000000000000000000000000000000000000000000000205c007f007f0"
        "0ff80ff81ffc1ffc1ffc1ffc1ffc1ffc1ffc0ff80ff807f007f00205c0000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "7403",
        "0100880400091b00068000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009403",
        "0100880400091b00078000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009503",
        "0100880400091b00088000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009a03",
        "0100880400091b00098000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "00000000000000000000000205c007f007f00ff80ff81ffc1ffc1ffc1ffc1ffc1ffc0f"
        "f80ff807f007f00205c000000000000000000000000000000000000000000000000000"
        "9b03",
        "0100880400091b000a8000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009803",
        "0100880400091b000b80000000000000000205c007f007f00ff80ff81ffc1ffc1ffc1f"
        "fc1ffc1ffc0ff80ff807f007f00205c000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "9903",
        "0100880400091b000c8000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009e03",
        "0100880400091b000d8000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "000000000207e007f00ff80ff81ffc1ffc1ffc1ffc1ffc0ff80ff807f00207e0000000"
        "7c03",
        "0100880400091b000e8000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000009c03",
        "0100880400091b000f8000000000000000000000000000000000000000000000000000"
        "000000000000000000000207e007f00ff80ff81ffc1ffc1ffc1ffc1ffc0ff80ff807f0"
        "0207e00000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "7e03",
        "0100880400091b00108000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "000000000207e007f00ff80ff81ffc1ffc1ffc1ffc1ffc0ff80ff807f00207e0000000"
        "6103",
        "0100880400091b00118000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000000000000000000000000000000000008303",
        "0100230400091b00121b00000000000000000000000000000000000000000000000000"
        "00001b03",
    ]

    confirm_chunks(
        SetAnimation(
            file_path_in_test_dir("test-animation.gif"),
            horizontal_alignment=HorizontalAlignment.LEFT,
        ).get_command_chunks(),
        correct_values,
    )
