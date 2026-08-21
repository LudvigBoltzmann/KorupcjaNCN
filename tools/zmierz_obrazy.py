#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spis rozmiarów obrazów z katalogu docs/ (dla atrybutów width/height).

    python3 tools/zmierz_obrazy.py

Zapisuje `tools/rozmiary-obrazow.json`. Dzięki temu `tools/build.py` może wpisać
do każdego `<img>` prawdziwe wymiary, nie mając zależności od biblioteki Pillow
(build w GitHub Actions instaluje tylko beautifulsoup4).

Prawdziwe width/height w kodzie strony likwidują „skakanie" tekstu podczas
wczytywania obrazów (Cumulative Layout Shift) — przeglądarka od razu wie,
ile miejsca zarezerwować.
"""

import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "tools", "rozmiary-obrazow.json")


def jpeg_size(path):
    """Wymiary JPEG bez zewnętrznych bibliotek (czytamy nagłówki SOFn)."""
    with open(path, "rb") as fh:
        if fh.read(2) != b"\xff\xd8":
            return None
        while True:
            marker = fh.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                return None
            code = marker[1]
            if code in (0xD8, 0x01) or 0xD0 <= code <= 0xD7:
                continue
            length = struct.unpack(">H", fh.read(2))[0]
            if 0xC0 <= code <= 0xCF and code not in (0xC4, 0xC8, 0xCC):
                fh.read(1)
                height, width = struct.unpack(">HH", fh.read(4))
                return width, height
            fh.seek(length - 2, os.SEEK_CUR)


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def gif_size(path):
    with open(path, "rb") as fh:
        head = fh.read(10)
    if head[:3] != b"GIF":
        return None
    return struct.unpack("<HH", head[6:10])


def main():
    sizes = {}
    for name in sorted(os.listdir(DOCS)):
        path = os.path.join(DOCS, name)
        if not os.path.isfile(path):
            continue
        low = name.lower()
        try:
            if low.endswith((".jpg", ".jpeg")):
                size = jpeg_size(path)
            elif low.endswith(".png"):
                size = png_size(path)
            elif low.endswith(".gif"):
                size = gif_size(path)
            else:
                continue
        except Exception:                                  # noqa: BLE001
            size = None
        if size:
            sizes["docs/" + name] = [size[0], size[1]]

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(sizes, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("Zmierzono %d obrazow -> %s" % (len(sizes), os.path.relpath(OUT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
