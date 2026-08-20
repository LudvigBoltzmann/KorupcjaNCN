#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pobiera fonty Inter i Source Serif 4 do repozytorium (hosting lokalny).

Uruchamiać tylko wtedy, gdy zmienia się zestaw fontów:

    python3 tools/pobierz_fonty.py

Skrypt zapisuje pliki .woff2 do `assets/fonts/` i generuje
`assets/fonts/fonts.css` z regułami @font-face (font-display: swap).
Dzięki temu witryna nie wysyła żadnego zapytania do fonts.googleapis.com
ani fonts.gstatic.com — bez utraty kroju pisma.

Zakres znaków: latin, latin-ext (polskie znaki) oraz cyrillic i cyrillic-ext
(wersja ukraińska witryny).
"""

import hashlib
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "fonts")
SUBSETS = ("latin", "latin-ext", "cyrillic", "cyrillic-ext")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
GOOGLE_CSS = ("https://fonts.googleapis.com/css2?"
              "family=Inter:wght@400;500;600&"
              "family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;"
              "0,8..60,700;1,8..60,400&display=swap")


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                  timeout=60).read()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    css = fetch(GOOGLE_CSS).decode("utf-8")

    faces = []
    total = 0
    downloaded = {}
    for block in re.split(r"(?=/\* [a-z-]+ \*/)", css):
        head = re.match(r"/\* ([a-z-]+) \*/", block.strip())
        if not head or head.group(1) not in SUBSETS:
            continue
        subset = head.group(1)
        face = re.search(r"@font-face\s*\{(.*?)\}", block, re.S)
        if not face:
            continue
        body = face.group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        style = re.search(r"font-style:\s*([a-z]+)", body).group(1)
        weight = re.search(r"font-weight:\s*([0-9 ]+)", body).group(1).strip()
        unicode_range = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()

        # Google dla fontow zmiennych podaje TEN SAM plik dla kilku grubosci.
        # Nazwa z odcisku tresci sprawia, ze taki plik lezy w repozytorium raz
        # i przegladarka pobiera go raz (a nie po jednym na kazda grubosc).
        data = downloaded.get(url)
        if data is None:
            data = fetch(url)
            downloaded[url] = data
        digest = hashlib.sha1(data).hexdigest()[:10]
        name = "%s-%s-%s.woff2" % (family.replace(" ", ""), subset, digest)
        path = os.path.join(OUT_DIR, name)
        if not os.path.exists(path):
            with open(path, "wb") as fh:
                fh.write(data)
            total += len(data)
        faces.append((family, style, weight, unicode_range, name))

    lines = ["/* Fonty hostowane lokalnie (Inter, Source Serif 4 — licencja OFL):",
             "   zero zapytan do fonts.googleapis.com i fonts.gstatic.com.",
             "   Plik generowany przez tools/pobierz_fonty.py — nie edytowac recznie. */"]
    for family, style, weight, unicode_range, name in faces:
        lines.append("@font-face{font-family:'%s';font-style:%s;font-weight:%s;"
                     "font-display:swap;src:url(/assets/fonts/%s) format('woff2');"
                     "unicode-range:%s;}" % (family, style, weight, name, unicode_range))
    with open(os.path.join(OUT_DIR, "fonts.css"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    unique = len({name for *_rest, name in faces})
    print("Regul @font-face: %d, unikalnych plikow woff2: %d (%.1f KB) w assets/fonts/"
          % (len(faces), unique, total / 1024))
    print("Zapisano assets/fonts/fonts.css")
    return 0


if __name__ == "__main__":
    sys.exit(main())
