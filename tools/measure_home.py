#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pomiar objetosci strony glownej PL: znaki, slowa, waga, sekcje.

Uzycie:
    python3 tools/measure_home.py [plik] [--json plik.json]

Domyslnie mierzy index.html w korzeniu repozytorium.
Mierzone jest:
  * waga pliku (bajty),
  * liczba znakow i slow WIDOCZNEJ TRESCI (bez <style>, <script>, <head>),
  * lista sekcji <section> w kolejnosci wystepowania z liczba znakow tekstu.
"""

import json
import os
import re
import sys

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def visible_text(node):
    for bad in node.find_all(["script", "style", "template", "noscript"]):
        bad.decompose()
    text = node.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)


def measure(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    size = os.path.getsize(path)

    soup = BeautifulSoup(raw, "html.parser")
    body = soup.body or soup
    for bad in body.find_all(["script", "style", "template", "noscript"]):
        bad.decompose()

    sections = []
    for sec in body.find_all("section"):
        if sec.find_parent("section"):
            continue
        heading = sec.find(["h1", "h2"])
        title = heading.get_text(" ", strip=True) if heading else "(bez naglowka)"
        text = re.sub(r"\s+", " ", sec.get_text(" ", strip=True))
        sections.append({
            "id": sec.get("id") or "",
            "class": " ".join(sec.get("class") or []),
            "title": title,
            "chars": len(text),
            "words": len(text.split()),
        })

    whole = re.sub(r"\s+", " ", body.get_text(" ", strip=True))
    return {
        "file": os.path.relpath(path, ROOT),
        "bytes": size,
        "html_chars": len(raw),
        "text_chars": len(whole),
        "text_words": len(whole.split()),
        "section_count": len(sections),
        "sections": sections,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else os.path.join(ROOT, "index.html")
    data = measure(path)

    print("Plik:            %s" % data["file"])
    print("Waga:            %d B (%.1f KB)" % (data["bytes"], data["bytes"] / 1024))
    print("Znaki HTML:      %d" % data["html_chars"])
    print("Znaki tresci:    %d" % data["text_chars"])
    print("Slowa tresci:    %d" % data["text_words"])
    print("Sekcji <section>: %d" % data["section_count"])
    print()
    print("%-32s %8s %7s  %s" % ("id sekcji", "znaki", "slowa", "naglowek"))
    for s in data["sections"]:
        print("%-32s %8d %7d  %s" % (s["id"] or "-", s["chars"], s["words"], s["title"][:70]))

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print("\nZapisano: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
