#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sprawdzenie kodow odpowiedzi wszystkich adresow witryny na serwerze lokalnym.

Uzycie:
    python3 -m http.server 8811 &        # w katalogu repozytorium
    python3 tools/sprawdz_adresy.py      # domyslnie http://localhost:8811

Kod wyjscia 0 = wszystkie adresy odpowiadaja kodem 200.
"""

import re
import sys
import urllib.error
import urllib.request
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8811"

EXTRA = ["/404.html", "/robots.txt", "/sitemap.xml", "/animation-en.html",
         "/visitor-count.json", "/docs/analiza_nagran_audio_kompletna.pdf",
         "/docs/kilarski-portrait-web.jpg"]


def main():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as fh:
        sitemap = fh.read()
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    paths = [re.sub(r"^https?://[^/]+", "", u) or "/" for u in locs] + EXTRA

    bad = []
    for path in paths:
        url = HOST + path
        try:
            code = urllib.request.urlopen(url, timeout=30).status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception as exc:                     # noqa: BLE001
            code = str(exc)
        print("%-6s %s" % (code, path))
        if code != 200:
            bad.append((code, path))

    print("\nSprawdzono adresow: %d, nie-200: %d" % (len(paths), len(bad)))
    for code, path in bad:
        print("  %s %s" % (code, path))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
