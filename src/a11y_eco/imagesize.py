"""Read the dimensions of an image from the first bytes of its file.

Only the headers are read, never the pixels: PNG, GIF, JPEG and WebP write their
dimensions near the start of the file. Anything else gives None: SVG has no size in
pixels, and other formats such as AVIF are not read.
"""

from __future__ import annotations

from a11y_eco.models import ImageSize

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_FRAMES = frozenset(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
_JPEG_STANDALONE = frozenset({0x01, 0xD8, *range(0xD0, 0xD8)})


def image_size(data: bytes) -> ImageSize | None:
    """Return the dimensions of an image, or None when they cannot be read.

    Args:
        data: The first bytes of the file; 64 KB are enough for every format read.

    Returns:
        The width and height in pixels, or None for another format, damaged or
        truncated data, or an image of zero pixels.
    """
    if data.startswith(PNG_SIGNATURE):
        size = _png(data)
    elif data.startswith((b"GIF87a", b"GIF89a")):
        size = _gif(data)
    elif data.startswith(b"\xff\xd8"):
        size = _jpeg(data)
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        size = _webp(data)
    else:
        size = None

    return size if size and size.pixels > 0 else None


def _png(data: bytes) -> ImageSize | None:
    if len(data) < 24 or data[12:16] != b"IHDR":
        return None

    return ImageSize(_big(data[16:20]), _big(data[20:24]))


def _gif(data: bytes) -> ImageSize | None:
    if len(data) < 10:
        return None

    return ImageSize(_little(data[6:8]), _little(data[8:10]))


def _jpeg(data: bytes) -> ImageSize | None:
    position = 2

    while position + 4 <= len(data):
        if data[position] != 0xFF:
            return None
        marker = data[position + 1]
        if marker == 0xFF:  # padding before a marker
            position += 1
            continue
        if marker in _JPEG_STANDALONE:
            position += 2
            continue
        if marker == 0xDA:  # image data without any frame: damaged
            return None
        if marker in _JPEG_FRAMES:
            if position + 9 > len(data):
                return None
            height = _big(data[position + 5 : position + 7])
            width = _big(data[position + 7 : position + 9])
            return ImageSize(width, height)
        position += 2 + _big(data[position + 2 : position + 4])

    return None


def _webp(data: bytes) -> ImageSize | None:
    chunk = data[12:16]

    if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
        return ImageSize(_little(data[26:28]) & 0x3FFF, _little(data[28:30]) & 0x3FFF)

    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = _little(data[21:25])
        return ImageSize((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)

    if chunk == b"VP8X" and len(data) >= 30:
        return ImageSize(_little(data[24:27]) + 1, _little(data[27:30]) + 1)

    return None


def _big(data: bytes) -> int:
    return int.from_bytes(data, "big")


def _little(data: bytes) -> int:
    return int.from_bytes(data, "little")
