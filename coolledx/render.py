"""Rendering functions for the CoolLEDx sign."""

import json
from typing import Optional, Tuple, Union

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


def render_text_to_image(
    text: str,
    default_color: str,
    font: str,
    font_height: int = DEFAULT_FONT_SIZE,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    color_markers: Union[Tuple[Optional[str], Optional[str]], str] = (
        DEFAULT_START_COLOR_MARKER,
        DEFAULT_END_COLOR_MARKER,
    ),
) -> Image.Image:
    """
    This will take text that has embedded color information, and render it to an
    image.  The text may have embedded colors specified between the defined
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
        if len(color_markers) == 1 or len(color_markers) == 2:
            left_marker = color_markers[0]
            right_marker = color_markers[1]
        else:
            raise ValueError(
                "color_markers must be a string of length 2 (2 chars) or a 2-tuple"
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
        background_color if background_color != DEFAULT_BACKGROUND_COLOR else 0,
    )
    draw = ImageDraw.Draw(img)

    truetype_font = ImageFont.truetype(font, font_height)

    # The parts are coming in (color, text).  Due to the way we've split the string,
    # any color changes should be applied AFTER we render the text.
    color = ImageColor.getrgb(default_color)
    for color_str, text in parts:
        if text is not None and len(text) > 0:
            draw.text((x_offset, y_offset), text, color, font=truetype_font)
            bounding_box = draw.textbbox((0, 0), text, font=truetype_font)
            x_offset += bounding_box[2]
            height = bounding_box[3]
            if height > y_max:
                y_max = height
        if color_str is not None:
            color = ImageColor.getrgb(color_str)

    del draw

    # crop the canvas
    return img.crop((0, 0, x_offset, y_max))


def get_separate_pixel_bytefields(
    img: Image.Image,
    output_width: int,
    output_height: int,
    bgColor=DEFAULT_BACKGROUND_COLOR,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
):
    """
    This generates the bytefields for the red, green, and blue components of the image.
    :param img:
    :param output_width: for a normal image, can be anything; animations must fit the
                         screen exactly
    :param output_height: this should be the screen height always
    :param bgColor: color to use for fill pixels (outside the image)
    :param horizontal_alignment:
    :param vertical_alignment:
    :return: the bytefields for the red, green, and blue components of the image
    """
    if output_height % 8 != 0:
        raise ValueError("target-height needs to be divisible by 8")

    # Declare these to stabilize type checking
    defaultPx: Tuple[int, int, int]
    px: Tuple[int, int, int]

    image_width, image_height = img.size
    defaultPx = ImageColor.getrgb(bgColor)  # type: ignore

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
    barr_R, barr_G, barr_B = bytearray(), bytearray(), bytearray()

    # temp values to shift the separate color bits while we iterate the pixels
    tmp_R, tmp_G, tmp_B = 0, 0, 0

    # iterate column from top to bottom
    # (first 2 bytes will be the left column, most significant bit will be pixel
    # on the top)
    for x in range(0, output_width):
        for y in range(0, output_height):
            # replace pixels outside image with default
            if (
                y < top_offset
                or x < left_offset
                or y >= image_height + top_offset
                or x >= image_width + left_offset
            ):
                px = defaultPx
            else:
                px = img.getpixel((x - left_offset, y - top_offset))

            # for each color, add one bit for the current pixel (i.e., 1 if
            # color-component is > 127)
            tmp_R = (tmp_R << 1) + int(round(px[0] / 255))
            tmp_G = (tmp_G << 1) + int(round(px[1] / 255))
            tmp_B = (tmp_B << 1) + int(round(px[2] / 255))

            # for every 8th pixel, add the byte to the bytefield and begin a new one
            if y % 8 == 7:
                barr_R.append(tmp_R)
                barr_G.append(tmp_G)
                barr_B.append(tmp_B)
                tmp_R, tmp_G, tmp_B = 0, 0, 0

    return barr_R, barr_G, barr_B


def get_separate_pixel_bytefields_for_animation(
    anim: Image.Image,
    sign_width: int,
    sign_height: int,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    width_treatment: WidthTreatment = WidthTreatment.SCALE,
    height_treatment: HeightTreatment = HeightTreatment.SCALE,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> Tuple[bytearray, bytearray, bytearray]:
    """
    This generates the bytefields for the red, green, and blue components
    :param anim:
    :param sign_width: all animations must be forced into exactly the sign width
    :param sign_height: should be the screen height always
    :param background_color: color to use for fill pixels (outside the image)
    :param width_treatment:
    :param height_treatment:
    :param horizontal_alignment:
    :param vertical_alignment:
    :return:
    """
    # TODO:  Use width_treatment and height_treatment to scale the animation to
    #  the sign's size
    is_animated = getattr(anim, "is_animated", False)
    if not is_animated:
        raise ValueError(f"image {anim} is not animated")

    # print ("animation has {} frames".format(anim.n_frames))

    combined_image = None

    animR, animG, animB = bytearray(), bytearray(), bytearray()

    for frame in range(0, anim.n_frames if hasattr(anim, "n_frames") else 1):  # type: ignore
        # switch to next frame
        anim.seek(frame)

        # it seems we have to care about applying the transparent pixels ourselves
        if combined_image is None:
            combined_image = anim.convert("RGBA")
        else:
            combined_image = Image.alpha_composite(combined_image, anim.convert("RGBA"))

        # Animations need to be force-fit to the size of the sign.
        frameR, frameG, frameB = get_separate_pixel_bytefields(
            combined_image,
            sign_width,
            sign_height,
            background_color,
            horizontal_alignment,
            vertical_alignment,
        )

        animR += frameR
        animG += frameG
        animB += frameB

    # returns all-pixels of all frames separately for each of the 3 color-components
    return animR, animG, animB


def create_image_output(
    image: Image.Image,
    sign_width: int,
    sign_height: int,
    text: Optional[str] = None,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> bytearray:
    # create the image payload
    pixel_payload = bytearray()
    # unknown 24 zero-bytes
    pixel_payload += bytearray(24)

    if text is not None:
        # length of string (pretty irrelevant because the image will be used anyway)
        pixel_payload += len(text).to_bytes(1, byteorder="big")

        # character string (pretty irrelevant because the image will be used anyway)
        char_metadata = bytearray(80)
        for i, _ in enumerate(text):
            if i < 80:
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
            output_width = sign_width if new_width < sign_width else new_width

    if new_width != width or new_height != height:
        # scale the image to the height of the sign
        image = image.resize((new_width, new_height))

    bR, bG, bB = get_separate_pixel_bytefields(
        image,
        output_width,
        sign_height,
        background_color,
        horizontal_alignment,
        vertical_alignment,
    )

    # all the pixel-bits RGB
    pixel_bits_all = bytearray().join([bR, bG, bB])
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
    color_markers: Union[Tuple[Optional[str], Optional[str]], str] = (
        DEFAULT_START_COLOR_MARKER,
        DEFAULT_END_COLOR_MARKER,
    ),
    render_as_text: bool = True,
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> bytearray:
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
    anim = Image.open(filename)
    frames = anim.n_frames if hasattr(anim, "n_frames") else 1  # type: ignore
    animR, animG, animB = get_separate_pixel_bytefields_for_animation(
        anim,
        sign_width=sign_width,
        sign_height=sign_height,
        background_color=background_color,
        width_treatment=width_treatment,
        height_treatment=height_treatment,
        horizontal_alignment=horizontal_alignment,
        vertical_alignment=vertical_alignment,
    )
    # all the pixel-bits RGB
    pixel_bits_all = bytearray().join([animR, animG, animB])

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


def create_JT_payload(
    filename: str,
    sign_width: int,
    sign_height: int,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> Tuple[bytearray, bool]:
    #    im = Image.open(filename).convert("RGB")
    render_as_image = False  # Until proven otherwise . .
    frames = 1  # Until proven otherwise . .
    speed = 0  # Until proven otherwise . .
    jtrgbdata = None  # Until proven otherwise . .

    with open(filename) as f:
        jtf = f.read()
        jt = json.loads(jtf)[0]  # json.loads(f)[0] JT data to dictionary
    if "aniData" in list(jt["data"]):
        jtrgbdata = jt["data"]["aniData"]
        render_as_image = False
    if "graffitiData" in list(jt["data"]):
        render_as_image = True
        jtrgbdata = jt["data"]["graffitiData"]
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

    if jtrgbdata is not None:
        pixel_bits_all = bytearray(jtrgbdata)
        # size of the pixel payload in its un-split form.
        pixel_payload += len(pixel_bits_all).to_bytes(2, byteorder="big")
        # all the pixel-bits
        pixel_payload += pixel_bits_all

    return pixel_payload, render_as_image
