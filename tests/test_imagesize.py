import struct

import pytest

from a11y_eco.imagesize import PNG_SIGNATURE, image_size
from a11y_eco.models import ImageSize


def png(width: int, height: int) -> bytes:
    return PNG_SIGNATURE + struct.pack(">I4sII", 13, b"IHDR", width, height) + b"\x08\x06"


def gif(width: int, height: int) -> bytes:
    return b"GIF89a" + struct.pack("<HH", width, height)


def jpeg(width: int, height: int, *, frame: int = 0xC0, exif: int = 0) -> bytes:
    app1 = b"\xff\xe1" + struct.pack(">H", exif + 2) + bytes(exif) if exif else b""
    sof = b"\xff" + bytes([frame]) + struct.pack(">HBHH", 17, 8, height, width)

    return b"\xff\xd8" + app1 + sof


def webp(chunk: bytes, payload: bytes) -> bytes:
    return b"RIFF" + struct.pack("<I", 4 + len(payload)) + b"WEBP" + chunk + payload


def webp_lossy(width: int, height: int) -> bytes:
    payload = bytes(4) + b"\x00\x00\x00" + b"\x9d\x01\x2a" + struct.pack("<HH", width, height)

    return webp(b"VP8 ", payload)


def webp_lossless(width: int, height: int) -> bytes:
    bits = (width - 1) | ((height - 1) << 14)

    return webp(b"VP8L", bytes(4) + b"\x2f" + struct.pack("<I", bits))


def webp_extended(width: int, height: int) -> bytes:
    canvas = (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")

    return webp(b"VP8X", bytes(8) + canvas)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(png(350, 300), id="png"),
        pytest.param(gif(350, 300), id="gif"),
        pytest.param(jpeg(350, 300), id="jpeg-baseline"),
        pytest.param(jpeg(350, 300, frame=0xC2), id="jpeg-progressive"),
        pytest.param(jpeg(350, 300, exif=40_000), id="jpeg-after-large-metadata"),
        pytest.param(webp_lossy(350, 300), id="webp-lossy"),
        pytest.param(webp_lossless(350, 300), id="webp-lossless"),
        pytest.param(webp_extended(350, 300), id="webp-extended"),
    ],
)
def test_reads_the_dimensions_of_each_format(data: bytes) -> None:
    assert image_size(data) == ImageSize(350, 300)


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', id="svg"),
        pytest.param(b"\x00\x00\x00\x1cftypavif", id="avif-not-read"),
        pytest.param(png(350, 300)[:20], id="truncated-png"),
        pytest.param(jpeg(350, 300)[:10], id="truncated-jpeg"),
        pytest.param(b"\xff\xd8\xff\xda\x00\x02", id="jpeg-data-before-frame"),
        pytest.param(b"\xff\xd8\x00\x00\x00\x00", id="jpeg-not-a-marker"),
        pytest.param(gif(0, 300), id="zero-pixels"),
    ],
)
def test_unreadable_images_give_none(data: bytes) -> None:
    assert image_size(data) is None


def test_jpeg_padding_and_standalone_markers_are_skipped() -> None:
    data = b"\xff\xd8" + b"\xff\xff" + b"\xff\xd0" + jpeg(64, 48)[2:]

    assert image_size(data) == ImageSize(64, 48)


def test_pixels_of_an_image() -> None:
    assert ImageSize(350, 300).pixels == 105_000
