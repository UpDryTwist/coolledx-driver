"""Rendering functions for the CoolLEDx sign."""

from __future__ import annotations

import json
import logging

from PIL import Image, ImageColor, ImageDraw, ImageFont

from coolledx import (
    DEFAULT_ANIMATION_SPEED,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_COLOR,
    DEFAULT_END_COLOR_MARKER,
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_START_COLOR_MARKER,
    HeightTreatment,
    HorizontalAlignment,
    VerticalAlignment,
    WidthTreatment,
)

LOGGER = logging.getLogger(__name__)

# Constants
PIXELS_PER_BYTE = 8
MAX_TEXT_LENGTH = 255
COLOR_MARKER_COUNT = 2


def render_text_to_image(
    text: str,
    default_color: str,
    font: str,
    font_height: int = DEFAULT_FONT_SIZE,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    color_markers: tuple[str | None, str | None] | str = (
        DEFAULT_START_COLOR_MARKER,
        DEFAULT_END_COLOR_MARKER,
    ),
) -> Image.Image:
    """
    Render text with embedded color information to an image.

    Take text that has embedded color information, and render it to an
    image. The text may have embedded colors specified between the defined
    color_markers (defaults to <>; you'd want to change if your text might include
    these characters). The text should be of the form:
    <color1>text1<color2>text2<color3>text3
    where <color1> is a color in #rrggbb format, and text1 is the text
    to render in that color. If no color is specified, the default_color is used.
    """
    y_offset = 1
    x_offset = 0
    y_max = y_offset

    if color_markers is None:
        parts = [(default_color, text)]
    else:
        parts = []
        if len(color_markers) == 1 or len(color_markers) == COLOR_MARKER_COUNT:
            left_marker = color_markers[0]
            right_marker = color_markers[1]
        else:
            raise ValueError(
                "color_markers must be a string of length 2 (2 chars) or a 2-tuple",
            )

        segments = text.split(right_marker)
        for segment in segments:
            pieces = segment.split(left_marker)
            if len(pieces) == 1:
                # It's just text.  Append w/o a color marker
                parts.append((None, pieces[0]))
            else:
                # We have a color marker and remainder is text
                color = pieces[-1]
                text = "".join(pieces[0:-1])
                parts.append((color, text))

    # create image canvas
    img = Image.new(
        "RGBA",
        (2048, 64),
        (
            ImageColor.getrgb(background_color)[0],
            ImageColor.getrgb(background_color)[1],
            ImageColor.getrgb(background_color)[2],
            255,
        ),
    )
    draw = ImageDraw.Draw(img)

    try:
        truetype_font = ImageFont.truetype(font, font_height)
    except Exception as e:  # noqa: BLE001
        LOGGER.warning(
            "Could not load font %s (falling back to default font): %s",
            font,
            e,
        )
        truetype_font = ImageFont.load_default(font_height)

    # The parts are coming in (color, text).  Due to the way we've split the string,
    # any color changes should be applied AFTER we render the text.
    color = ImageColor.getrgb(default_color)
    for color_str, text in parts:
        if text is not None and len(text) > 0:
            draw.text((x_offset, y_offset), text, color, font=truetype_font)
            bounding_box = draw.textbbox((0, 0), text, font=truetype_font)
            x_offset += bounding_box[2]
            height = bounding_box[3]
            y_max = max(y_max, height)
        if color_str is not None:
            color = ImageColor.getrgb(color_str)

    del draw

    # crop the canvas
    return img.crop(
        (0, 0, x_offset, y_max + 1),
    )  # pixel vertical adjustment prevents bottom text cut off


def get_separate_pixel_bytefields(
    img: Image.Image,
    output_width: int,
    output_height: int,
    bg_color: str = DEFAULT_BACKGROUND_COLOR,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> tuple[bytearray, bytearray, bytearray]:
    """
    Generate the bytefields for the red, green, and blue components of the image.

    :param img: The image to process
    :param output_width: For a normal image, can be anything; animations must fit the
                         screen exactly
    :param output_height: This should be the screen height always
    :param bg_color: Color to use for fill pixels (outside the image)
    :param horizontal_alignment: How to align the image horizontally
    :param vertical_alignment: How to align the image vertically
    :return: The bytefields for the red, green, and blue components of the image
    """
    if output_height % PIXELS_PER_BYTE != 0:
        raise ValueError("target-height needs to be divisible by 8")

    # Declare these to stabilize type checking
    default_px: tuple[int, int, int]
    px: tuple[int, int, int]

    image_width, image_height = img.size
    default_px = ImageColor.getrgb(bg_color)  # type: ignore[misc]

    left_offset = 0
    top_offset = 0

    # Figure out justification on the width
    if horizontal_alignment == HorizontalAlignment.LEFT:
        # left justified, pretty much just leave it as it is
        left_offset = 0
    elif horizontal_alignment == HorizontalAlignment.CENTER:
        if image_width < output_width:
            left_offset = (output_width - image_width) // 2
        elif image_width > output_width:
            overflow = (image_width - output_width) // 2
            img = img.crop((overflow, 0, image_width - overflow, image_height))
    elif horizontal_alignment == HorizontalAlignment.RIGHT:
        if image_width < output_width:
            left_offset = output_width - image_width
        elif image_width > output_width:
            # We're going to crop it so it right-justifies
            img = img.crop((image_width - output_width, 0, image_width, image_height))

    if vertical_alignment == VerticalAlignment.TOP:
        # top justified, pretty much just leave it as it is
        top_offset = 0
    elif vertical_alignment == VerticalAlignment.CENTER:
        if image_height < output_height:
            top_offset = (output_height - image_height) // 2
        elif image_height > output_height:
            overflow = (image_height - output_height) // 2
            img = img.crop((0, overflow, image_width, image_height - overflow))
    elif vertical_alignment == VerticalAlignment.BOTTOM:
        if image_height < output_height:
            top_offset = output_height - image_height
        elif image_height > output_height:
            # We're going to crop it so it bottom-justifies
            img = img.crop((0, image_height - output_height, image_width, image_height))

    # buffer to hold the separate pixels
    barr_r, barr_g, barr_b = bytearray(), bytearray(), bytearray()

    # temp values to shift the separate color bits while we iterate the pixels
    tmp_r, tmp_g, tmp_b = 0, 0, 0

    # iterate column from top to bottom
    # (first 2 bytes will be the left column, most significant bit will be pixel
    # on the top)
    for x in range(output_width):
        for y in range(output_height):
            # replace pixels outside image with default
            if (
                y < top_offset
                or x < left_offset
                or y >= image_height + top_offset
                or x >= image_width + left_offset
            ):
                px = default_px
            else:
                px = img.getpixel((x - left_offset, y - top_offset))  # type: ignore[misc]

            # for each color, add one bit for the current pixel (i.e., 1 if
            # color-component is > 127)
            tmp_r = (tmp_r << 1) + round(px[0] / 255)
            tmp_g = (tmp_g << 1) + round(px[1] / 255)
            tmp_b = (tmp_b << 1) + round(px[2] / 255)

            # for every 8th pixel, add the byte to the bytefield and begin a new one
            if y % PIXELS_PER_BYTE == (PIXELS_PER_BYTE - 1):  # Every 8th pixel
                barr_r.append(tmp_r)
                barr_g.append(tmp_g)
                barr_b.append(tmp_b)
                tmp_r, tmp_g, tmp_b = 0, 0, 0

    return barr_r, barr_g, barr_b


def get_separate_pixel_bytefields_for_animation(
    anim: Image.Image,
    sign_width: int,
    sign_height: int,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    _width_treatment: WidthTreatment = WidthTreatment.SCALE,
    _height_treatment: HeightTreatment = HeightTreatment.SCALE,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> tuple[bytearray, bytearray, bytearray]:
    """
    Generate the bytefields for the red, green, and blue components.

    :param anim: The animation image to process
    :param sign_width: All animations must be forced into exactly the sign width
    :param sign_height: Should be the screen height always
    :param background_color: Color to use for fill pixels (outside the image)
    :param width_treatment: How to treat width scaling
    :param height_treatment: How to treat height scaling
    :param horizontal_alignment: How to align horizontally
    :param vertical_alignment: How to align vertically
    :return: Tuple of red, green, blue bytefields
    """
    # TODO:  Use width_treatment and height_treatment to scale the animation to
    #  the sign's size
    is_animated = getattr(anim, "is_animated", False)
    if not is_animated:
        raise ValueError(f"image {anim} is not animated")

    # print ("animation has {} frames".format(anim.n_frames))

    combined_image = None

    anim_r, anim_g, anim_b = bytearray(), bytearray(), bytearray()

    for frame in range(anim.n_frames if hasattr(anim, "n_frames") else 1):  # type: ignore[misc]
        # switch to next frame
        anim.seek(frame)

        # it seems we have to care about applying the transparent pixels ourselves
        if combined_image is None:
            combined_image = anim.convert("RGBA")
        else:
            combined_image = Image.alpha_composite(combined_image, anim.convert("RGBA"))

        # Animations need to be force-fit to the size of the sign.
        frame_r, frame_g, frame_b = get_separate_pixel_bytefields(
            combined_image,
            sign_width,
            sign_height,
            background_color,
            horizontal_alignment,
            vertical_alignment,
        )

        anim_r += frame_r
        anim_g += frame_g
        anim_b += frame_b

    # returns all-pixels of all frames separately for each of the 3 color-components
    return anim_r, anim_g, anim_b


def create_image_output(
    image: Image.Image,
    sign_width: int,
    sign_height: int,
    text: str | None = None,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> bytearray:
    """Create image output payload for the sign."""
    # create the image payload
    pixel_payload = bytearray()
    # unknown 24 zero-bytes
    pixel_payload += bytearray(24)

    if text is not None:
        buffer_length = 80
        if len(text) > MAX_TEXT_LENGTH:
            LOGGER.warning(
                "Text message length exceeds 255 characters; may not work on all signs.  %s",
                text,
            )
            pixel_payload += len(text).to_bytes(2, byteorder="big")
            buffer_length = 79
        else:
            pixel_payload += len(text).to_bytes(1, byteorder="big")

        # character string (pretty irrelevant because the image will be used anyway)
        char_metadata = bytearray(buffer_length)
        for i, _ in enumerate(text):
            if i < buffer_length:
                char_metadata[i] = 0x30
        pixel_payload += char_metadata

    width, height = image.size
    new_width, new_height = width, height
    output_width = width

    if width_treatment == WidthTreatment.SCALE:
        new_width = sign_width
        output_width = sign_width
        new_height = int(sign_width * height / width)
    elif width_treatment == WidthTreatment.CROP_PAD:
        output_width = sign_width

    if height_treatment == HeightTreatment.SCALE:
        new_height = sign_height
        if width_treatment == WidthTreatment.LEFT_AS_IS:
            new_width = int(sign_height * width / height)
            output_width = max(new_width, sign_width)

    if new_width != width or new_height != height:
        # scale the image to the height of the sign
        image = image.resize((new_width, new_height))

    b_r, b_g, b_b = get_separate_pixel_bytefields(
        image,
        output_width,
        sign_height,
        background_color,
        horizontal_alignment,
        vertical_alignment,
    )

    # all the pixel-bits RGB
    pixel_bits_all = bytearray().join([b_r, b_g, b_b])
    # size of the pixel payload in its un-split form.
    pixel_payload += len(pixel_bits_all).to_bytes(2, byteorder="big")
    # all the pixel-bits
    pixel_payload += pixel_bits_all

    return pixel_payload


def create_text_payload(
    txt: str,
    sign_width: int,
    sign_height: int,
    font: str = DEFAULT_FONT,
    default_color: str = DEFAULT_COLOR,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    font_height: int = DEFAULT_FONT_SIZE,
    color_markers: tuple[str | None, str | None] | str = (
        DEFAULT_START_COLOR_MARKER,
        DEFAULT_END_COLOR_MARKER,
    ),
    *,
    render_as_text: bool = True,
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> bytearray:
    """Create text payload for the sign."""
    im = render_text_to_image(
        txt,
        default_color=default_color,
        background_color=background_color,
        font=font,
        font_height=font_height,
        color_markers=color_markers,
    )

    return create_image_output(
        im,
        sign_width=sign_width,
        sign_height=sign_height,
        text=txt if render_as_text else None,
        background_color=background_color,
        width_treatment=width_treatment,
        height_treatment=height_treatment,
        horizontal_alignment=horizontal_alignment,
        vertical_alignment=vertical_alignment,
    )


def create_image_payload(
    filename: str,
    sign_width: int,
    sign_height: int,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> bytearray:
    """Create image payload from file for the sign."""
    im = Image.open(filename).convert("RGB")
    return create_image_output(
        im,
        sign_width=sign_width,
        sign_height=sign_height,
        text=None,
        background_color=background_color,
        width_treatment=width_treatment,
        height_treatment=height_treatment,
        horizontal_alignment=horizontal_alignment,
        vertical_alignment=vertical_alignment,
    )


def create_animation_payload(
    filename: str,
    sign_width: int,
    sign_height: int,
    speed: int = DEFAULT_ANIMATION_SPEED,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    width_treatment: WidthTreatment = WidthTreatment.SCALE,
    height_treatment: HeightTreatment = HeightTreatment.SCALE,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> bytearray:
    """Create animation payload from file for the sign."""
    anim = Image.open(filename)
    frames = anim.n_frames if hasattr(anim, "n_frames") else 1  # type: ignore[misc]
    anim_r, anim_g, anim_b = get_separate_pixel_bytefields_for_animation(
        anim,
        sign_width,
        sign_height,
        background_color,
        width_treatment,
        height_treatment,
        horizontal_alignment,
        vertical_alignment,
    )
    # all the pixel-bits RGB
    pixel_bits_all = bytearray().join([anim_r, anim_g, anim_b])

    # create the image payload
    pixel_payload = bytearray()
    # unknown 24 zero-bytes
    pixel_payload += bytearray(24)
    # number of frames
    pixel_payload += frames.to_bytes(1, byteorder="big")
    # speed (16-bit)
    pixel_payload += speed.to_bytes(2, byteorder="big")
    # all the pixel-bits
    pixel_payload += pixel_bits_all

    return pixel_payload


def create_jt_payload(
    filename: str,
    _sign_width: int,
    _sign_height: int,
    _background_color: str = DEFAULT_BACKGROUND_COLOR,
    _width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    _height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    _horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    _vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> tuple[bytearray, bool]:
    """Create JT payload from file for the sign."""
    #    im = Image.open(filename).convert("RGB")
    render_as_image = False  # Until proven otherwise . .
    frames = 1  # Until proven otherwise . .
    speed = 0  # Until proven otherwise . .
    jt_rgb_data = None  # Until proven otherwise . .

    with open(filename) as f:
        jtf = f.read()
        jt = json.loads(jtf)[0]  # json.loads(f)[0] JT data to dictionary
    if "aniData" in list(jt["data"]):
        jt_rgb_data = jt["data"]["aniData"]
        render_as_image = False
    if "graffitiData" in list(jt["data"]):
        render_as_image = True
        jt_rgb_data = jt["data"]["graffitiData"]
    # Unused - prefix with _ to suppress warning
    _sign_width = jt["data"]["pixelWidth"]
    _sign_height = jt["data"]["pixelHeight"]
    if "frameNum" in list(jt["data"]):
        frames = jt["data"]["frameNum"]
    if "delays" in list(jt["data"]):
        speed = jt["data"]["delays"]

    # create the image payload
    pixel_payload = bytearray()
    # unknown 24 zero-bytes
    pixel_payload += bytearray(24)
    # all the pixel-bits RGB
    # pixel_bits_all = bytearray().join([bR, bG, bB])

    # --------animation-------------------
    if not render_as_image:
        # number of frames
        pixel_payload += frames.to_bytes(1, byteorder="big")
        # speed (16-bit)
        pixel_payload += speed.to_bytes(2, byteorder="big")
    # --------animation-------------------

    if jt_rgb_data is not None:
        pixel_bits_all = bytearray(jt_rgb_data)
        # size of the pixel payload in its un-split form.
        pixel_payload += len(pixel_bits_all).to_bytes(2, byteorder="big")
        # all the pixel-bits
        pixel_payload += pixel_bits_all

    return pixel_payload, render_as_image
