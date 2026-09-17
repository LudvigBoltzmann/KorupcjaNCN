#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fonty witryny: pobranie, obcięcie do używanych znaków i hosting lokalny.

Uruchamiać tylko wtedy, gdy zmienia się zestaw fontów albo pojawiają się nowe
znaki w treści:

    python3 tools/pobierz_fonty.py

Co robi:
1. pobiera z Google Fonts pliki woff2 rodzin Inter i Source Serif 4
   (te same, których witryna używała dotąd — krój się nie zmienia),
2. odrzuca duplikaty (dla fontów zmiennych Google podaje jeden plik dla kilku
   grubości),
3. **obcina każdy plik do znaków faktycznie potrzebnych**: wszystkie znaki
   występujące w wygenerowanych stronach witryny plus stały zapas
   (podstawowa łacina, znaki polskie, francuskie i niemieckie, typografia,
   strzałki oraz cyrylica ukraińska dla wersji /uk/),
4. zapisuje wynik do `assets/fonts/` i generuje `assets/fonts/fonts.css`.

Efekt: żadnego zapytania do fonts.googleapis.com ani fonts.gstatic.com
i kilkakrotnie mniejsze pliki fontów.
"""

import glob
import hashlib
import os
import re
import sys
import unicodedata
import urllib.request

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "fonts")
CACHE_DIR = os.path.join(ROOT, ".fonts-cache")

SUBSETS = ("latin", "latin-ext", "cyrillic", "cyrillic-ext")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
GOOGLE_CSS = ("https://fonts.googleapis.com/css2?"
              "family=Inter:wght@400;500;600&"
              "family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;"
              "0,8..60,700;1,8..60,400&display=swap")

# Stały zapas znaków — niezależny od dzisiejszej treści, żeby dopisanie akapitu
# nie wymagało od razu ponownego obcinania fontów.
SAFETY_RANGES = [
    (0x0020, 0x007E),   # podstawowa łacina, cyfry, interpunkcja
    (0x00A0, 0x00FF),   # łacina-1: é à ü ö ä ß ç ñ, twarda spacja, °, «»
    (0x0100, 0x017F),   # łacina rozszerzona A: ą ć ę ł ń ó ś ź ż, č š ž, ő ű
    (0x0192, 0x0192),
    (0x02C6, 0x02DD),   # akcenty samodzielne
    (0x2010, 0x2015),   # dywizy i pauzy
    (0x2018, 0x201F),   # cudzysłowy, w tym polskie „ ”
    (0x2020, 0x2022),   # † ‡ •
    (0x2026, 0x2026),   # …
    (0x2030, 0x2030),   # ‰
    (0x2039, 0x203A),   # ‹ ›
    (0x2044, 0x2044),
    (0x2060, 0x2060),
    (0x20AC, 0x20AC),   # €
    (0x2116, 0x2116),   # №
    (0x2122, 0x2122),   # ™
    (0x2190, 0x2199),   # strzałki ← ↑ → ↓
    (0x21B5, 0x21B5),
    (0x2212, 0x2212),   # minus
    (0x25B6, 0x25B6),   # ▶
    (0x0400, 0x045F),   # cyrylica ukraińska/rosyjska
    (0x0490, 0x0491),   # ґ
]

RANGE_RE = re.compile(r"U\+([0-9A-Fa-f]+)(?:-([0-9A-Fa-f]+))?")

# Ograniczenie osi fontow zmiennych. Pliki Google zawieraja caly wachlarz
# grubosci 100-900 i os rozmiaru optycznego 8-60 pt, a witryna uzywa tylko
# kilku grubosci. Przypiecie osi `opsz` i zawezenie `wght` zmniejsza pliki
# kilkukrotnie, nie zmieniajac kroju pisma.
AXIS_LIMITS = {
    "Inter": {"wght": (400, 600)},
    "Source Serif 4": {"opsz": 20, "wght": (400, 700)},
}


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                  timeout=90).read()


def parse_unicode_range(text):
    """'U+0000-00FF, U+0131' -> zbiór numerów znaków."""
    out = set()
    for start, end in RANGE_RE.findall(text):
        lo = int(start, 16)
        hi = int(end, 16) if end else lo
        out.update(range(lo, hi + 1))
    return out


def safety_set():
    out = set()
    for lo, hi in SAFETY_RANGES:
        out.update(range(lo, hi + 1))
    return out


def used_in_site():
    """Znaki występujące w wygenerowanych stronach (tekst + atrybuty widoczne)."""
    chars = set()
    patterns = ["index.html", "*/index.html", "*/*/index.html", "404.html"]
    seen = set()
    for pattern in patterns:
        for path in glob.glob(os.path.join(ROOT, pattern)):
            if path in seen or os.sep + "assets" + os.sep in path:
                continue
            seen.add(path)
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
            html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
            html = re.sub(r"<[^>]+>", " ", html)
            chars.update(ord(c) for c in html)
    # znaki złożone: dorzuć formy rozłożone (na wypadek kombinowanych akcentów)
    extra = set()
    for cp in list(chars):
        for c in unicodedata.normalize("NFD", chr(cp)):
            extra.add(ord(c))
    chars.update(extra)
    return chars


def compact_ranges(codepoints):
    """Zbiór numerów znaków -> zapis 'U+20-7E, U+A0' dla unicode-range."""
    out = []
    for cp in sorted(codepoints):
        if out and cp == out[-1][1] + 1:
            out[-1][1] = cp
        else:
            out.append([cp, cp])
    parts = []
    for lo, hi in out:
        parts.append("U+%04X" % lo if lo == hi else "U+%04X-%04X" % (lo, hi))
    return ", ".join(parts)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    wanted = safety_set() | used_in_site()
    print("Znaków w treści witryny + zapas: %d" % len(wanted))

    css = fetch(GOOGLE_CSS).decode("utf-8")

    faces = []
    downloaded = {}
    for block in re.split(r"(?=/\* [a-z-]+ \*/)", css):
        head = re.match(r"/\* ([a-z-]+) \*/", block.strip())
        if not head or head.group(1) not in SUBSETS:
            continue
        subset_name = head.group(1)
        face = re.search(r"@font-face\s*\{(.*?)\}", block, re.S)
        if not face:
            continue
        body = face.group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        style = re.search(r"font-style:\s*([a-z]+)", body).group(1)
        weight = re.search(r"font-weight:\s*([0-9 ]+)", body).group(1).strip()
        declared = parse_unicode_range(
            re.search(r"unicode-range:\s*([^;]+);", body).group(1))

        if url not in downloaded:
            raw_path = os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest() + ".woff2")
            if not os.path.exists(raw_path):
                with open(raw_path, "wb") as fh:
                    fh.write(fetch(url))
            downloaded[url] = raw_path
        faces.append({"family": family, "style": style, "weight": weight,
                      "subset": subset_name, "declared": declared,
                      "source": downloaded[url]})

    # Obcięcie: jeden plik na (źródłowy plik + zakres znaków).
    for old in glob.glob(os.path.join(OUT_DIR, "*.woff2")):
        os.unlink(old)

    built = {}
    total_before = 0
    total_after = 0
    for face in faces:
        font = TTFont(face["source"])
        cmap = set()
        for table in font["cmap"].tables:
            cmap.update(table.cmap.keys())
        font.close()

        target = sorted(face["declared"] & cmap & wanted)
        if not target:
            face["skip"] = True
            continue

        key = (face["source"], tuple(target))
        if key not in built:
            digest = hashlib.sha1(
                (face["source"] + repr(target)).encode()).hexdigest()[:10]
            name = "%s-%s-%s.woff2" % (face["family"].replace(" ", ""),
                                       face["subset"], digest)
            out_path = os.path.join(OUT_DIR, name)

            # 1) zawezenie osi fontu zmiennego (mniej danych o wariantach)
            source = face["source"]
            limits = AXIS_LIMITS.get(face["family"])
            trimmed = None
            if limits:
                font = TTFont(source)
                if "fvar" in font:
                    usable = {tag: value for tag, value in limits.items()
                              if tag in {a.axisTag for a in font["fvar"].axes}}
                    if usable:
                        instancer.instantiateVariableFont(
                            font, usable, inplace=True, updateFontNames=False)
                        trimmed = os.path.join(
                            CACHE_DIR, "instance-%s.ttf" % digest)
                        font.save(trimmed)
                        source = trimmed
                font.close()

            # 2) obciecie do potrzebnych znakow
            subset.main([source,
                         "--unicodes=%s" % ",".join("U+%04X" % cp for cp in target),
                         "--layout-features=kern,liga,clig,calt",
                         "--flavor=woff2",
                         "--no-hinting",
                         "--desubroutinize",
                         "--output-file=%s" % out_path])
            if trimmed and os.path.exists(trimmed):
                os.unlink(trimmed)
            built[key] = name
            total_before += os.path.getsize(face["source"])
            total_after += os.path.getsize(out_path)
        face["file"] = built[key]
        face["target"] = target

    lines = ["/* Fonty hostowane lokalnie i obciete do znakow uzywanych na witrynie.",
             "   Inter i Source Serif 4 (licencja OFL). Zero zapytan do",
             "   fonts.googleapis.com i fonts.gstatic.com.",
             "   Plik generowany przez tools/pobierz_fonty.py — nie edytowac recznie. */"]
    for face in faces:
        if face.get("skip"):
            continue
        lines.append("@font-face{font-family:'%s';font-style:%s;font-weight:%s;"
                     "font-display:swap;src:url(/assets/fonts/%s) format('woff2');"
                     "unicode-range:%s;}"
                     % (face["family"], face["style"], face["weight"],
                        face["file"], compact_ranges(face["target"])))
    with open(os.path.join(OUT_DIR, "fonts.css"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print("Regul @font-face: %d, unikalnych plikow: %d" %
          (len([f for f in faces if not f.get("skip")]), len(built)))
    print("Rozmiar plikow fontow: %.1f KB -> %.1f KB (%.0f%% mniej)" %
          (total_before / 1024, total_after / 1024,
           100 - 100.0 * total_after / max(total_before, 1)))
    print("Zapisano assets/fonts/fonts.css")
    return 0


if __name__ == "__main__":
    sys.exit(main())
