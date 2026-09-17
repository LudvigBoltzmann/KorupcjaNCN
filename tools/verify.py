#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Weryfikacja wygenerowanych stron KorupcjaNCN (punkt 10 specyfikacji Pakietu B).

Uruchomienie:
    python3 tools/verify.py [sciezka/raportu.txt]

Kod wyjscia 0 = raport bez bledow.
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import (BASE, LANGS, LANG_URL, SECTIONS, SITE, HTML_LANG,  # noqa: E402
                   CONTENT_PAGES, RECORDINGS, HUBS, NAV_TABS, sitemap_slugs)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# `#top` i puste `#` sa obslugiwane natywnie przez przegladarki (gora dokumentu).
NATIVE_FRAGMENTS = {"", "top"}

PAGES = [("index.html", "pl")]
PAGES += [("%s/index.html" % l, l) for l in LANGS if l != "pl"]
PAGES += [("%s/index.html" % h["slug"], "pl") for h in HUBS]
PAGES += [("%s/index.html" % p["slug"], "pl") for p in CONTENT_PAGES]
PAGES += [("%s/index.html" % r["slug"], "pl") for r in RECORDINGS]
PAGES += [("skorowidz/index.html", "pl")]
PAGES += [("%s/skorowidz/index.html" % l, l) for l in LANGS if l != "pl"]

LANG_PAGES = ["index.html"] + ["%s/index.html" % l for l in LANGS if l != "pl"]


class Report:
    def __init__(self):
        self.lines = []
        self.errors = 0

    def head(self, text):
        self.lines.append("")
        self.lines.append(text)
        self.lines.append("-" * len(text))

    def ok(self, text):
        self.lines.append("  OK    %s" % text)

    def info(self, text):
        self.lines.append("        %s" % text)

    def fail(self, text):
        self.lines.append("  BLAD  %s" % text)
        self.errors += 1

    def text(self):
        return "\n".join(self.lines).lstrip("\n") + "\n"


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        raw = fh.read()
    return raw, BeautifulSoup(raw, "html.parser")


def url_to_path(url):
    """/KorupcjaNCN/foo/bar.pdf -> foo/bar.pdf ; /KorupcjaNCN/en/ -> en/index.html"""
    path = unquote(urlparse(url).path)
    rel = path[len(BASE):].lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    return rel


def check_parsing_and_ids(rep):
    rep.head("1. Parsowanie stron i unikalnosc atrybutow id")
    for path, _lang in PAGES + [("404.html", "pl")]:
        try:
            raw, soup = load(path)
        except Exception as exc:  # pragma: no cover
            rep.fail("%s: blad parsowania: %s" % (path, exc))
            continue
        if soup.find("html") is None or soup.find("body") is None:
            rep.fail("%s: brak <html> lub <body>" % path)
            continue
        ids = [t["id"] for t in soup.find_all(attrs={"id": True})]
        dupes = sorted(k for k, v in Counter(ids).items() if v > 1)
        if dupes:
            rep.fail("%s: zduplikowane id: %s" % (path, ", ".join(dupes)))
        else:
            rep.ok("%s — parsuje sie, %d unikalnych id" % (path, len(ids)))


def check_head_uniqueness(rep):
    rep.head("2. title / canonical / description / <html lang>")
    for path, lang in PAGES:
        raw, soup = load(path)
        titles = soup.find_all("title")
        canon = soup.find_all("link", attrs={"rel": ["canonical"]})
        desc = soup.find_all("meta", attrs={"name": "description"})
        problems = []
        if len(titles) != 1:
            problems.append("<title>: %d" % len(titles))
        if len(canon) != 1:
            problems.append("canonical: %d" % len(canon))
        if len(desc) != 1:
            problems.append("meta description: %d" % len(desc))
        if soup.html.get("lang") != HTML_LANG[lang]:
            problems.append("html lang=%r (oczekiwano %r)"
                            % (soup.html.get("lang"), HTML_LANG[lang]))
        expected_canonical = SITE + "/" + os.path.dirname(path)
        expected_canonical = expected_canonical.rstrip("/") + "/"
        if canon and canon[0].get("href") != expected_canonical:
            problems.append("canonical=%s (oczekiwano %s)"
                            % (canon[0].get("href"), expected_canonical))
        if soup.find_all("meta", attrs={"name": "keywords"}):
            problems.append("pozostal meta keywords")
        if problems:
            rep.fail("%s: %s" % (path, "; ".join(problems)))
        else:
            rep.ok("%s — lang=%s, canonical=%s" % (path, HTML_LANG[lang],
                                                   expected_canonical))


def check_single_language(rep):
    rep.head("3. Jeden jezyk blokow .lang-block na stronie")
    for path, lang in PAGES:
        raw, soup = load(path)
        found = Counter()
        for block in soup.find_all(attrs={"data-lang": True}):
            found[block["data-lang"]] += 1
        other = {k: v for k, v in found.items() if k != lang}
        stray_nav = set()
        for tag in soup.find_all(True):
            for cls in tag.get("class") or []:
                if re.fullmatch(r"nav-(pl|en|fr|de|uk)", cls) and cls != "nav-" + lang:
                    stray_nav.add(cls)
        if other:
            rep.fail("%s: obce bloki jezykowe: %s" % (path, dict(other)))
        elif stray_nav:
            rep.fail("%s: obce elementy nawigacji: %s" % (path, sorted(stray_nav)))
        else:
            rep.ok("%s — %d blokow, wylacznie data-lang=%s" % (path, found[lang], lang))


def check_local_links(rep):
    rep.head("4. Lokalne linki wskazuja istniejace pliki")
    missing = Counter()
    checked = 0
    for path, _lang in PAGES + [("404.html", "pl")]:
        raw, soup = load(path)
        for tag in soup.find_all(True):
            for attr in ("href", "src", "poster"):
                value = tag.get(attr)
                if not isinstance(value, str) or not value.startswith(BASE + "/"):
                    continue
                if value.startswith("//"):  # zasob zewnetrzny (protocol-relative)
                    continue
                checked += 1
                target = url_to_path(value)
                if not os.path.exists(os.path.join(ROOT, target)):
                    missing[target] += 1
    if missing:
        for target, count in sorted(missing.items()):
            rep.fail("brak pliku: %s (%d odwolan)" % (target, count))
    else:
        rep.ok("sprawdzono %d odwolan — wszystkie pliki istnieja" % checked)


def check_anchors(rep):
    rep.head("5. Kotwice #... maja odpowiadajace id na tej samej stronie")
    for path, _lang in PAGES + [("404.html", "pl")]:
        raw, soup = load(path)
        ids = {t["id"] for t in soup.find_all(attrs={"id": True})}
        orphans = Counter()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href.startswith("#"):
                continue
            frag = href[1:]
            if frag in NATIVE_FRAGMENTS or frag in ids:
                continue
            orphans[frag] += 1
        if orphans:
            rep.fail("%s: osierocone kotwice: %s"
                     % (path, ", ".join("#%s (%d)" % (k, v)
                                        for k, v in sorted(orphans.items()))))
        else:
            rep.ok("%s — brak osieroconych kotwic" % path)


def check_sizes(rep):
    rep.head("6. Rozmiary plikow")
    before = os.path.getsize(os.path.join(ROOT, "src", "index.src.html"))
    after = os.path.getsize(os.path.join(ROOT, "index.html"))
    rep.info("index.html PRZED (src/index.src.html): %8.1f KB" % (before / 1024))
    rep.info("index.html PO  (strona glowna PL)    : %8.1f KB  (%.1f%% zrodla)"
             % (after / 1024, 100.0 * after / before))
    for path, _lang in PAGES[1:] + [("404.html", "pl"), ("sitemap.xml", "pl")]:
        rep.info("%-38s %8.1f KB"
                 % (path, os.path.getsize(os.path.join(ROOT, path)) / 1024))


def check_hreflang(rep):
    rep.head("7. Klaster hreflang (5 stron jezykowych x 6 wpisow)")
    expected = {l: LANG_URL[l] for l in LANGS}
    expected["x-default"] = LANG_URL["pl"]
    for path in LANG_PAGES:
        raw, soup = load(path)
        found = {}
        duplicated = []
        for link in soup.find_all("link", attrs={"rel": ["alternate"]}):
            key = link.get("hreflang")
            if key in found:
                duplicated.append(key)
            found[key] = link.get("href")
        if duplicated:
            rep.fail("%s: powtorzone hreflang: %s" % (path, duplicated))
        elif found != expected:
            rep.fail("%s: klaster niezgodny: %s" % (path, found))
        else:
            rep.ok("%s — 6 wpisow, wszystkie URL-e zgodne" % path)
    for path, _lang in PAGES[len(LANG_PAGES):]:
        raw, soup = load(path)
        count = len(soup.find_all("link", attrs={"rel": ["alternate"]}))
        if count:
            rep.fail("%s: strona sekcyjna nie powinna miec hreflang (%d wpisow)"
                     % (path, count))
        else:
            rep.ok("%s — brak hreflang (zgodnie ze specyfikacja)" % path)


def check_no_hash_leftovers(rep):
    rep.head("8. Brak pozostalosci #pl/#en w hreflang i sitemap.xml")
    bad = False
    for path, _lang in PAGES:
        raw, soup = load(path)
        for link in soup.find_all("link", attrs={"rel": ["alternate"]}):
            if "#" in (link.get("href") or ""):
                rep.fail("%s: link[rel=alternate] z fragmentem: %s" % (path, link["href"]))
                bad = True
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as fh:
        sitemap = fh.read()
    frags = re.findall(r"<(?:loc|xhtml:link[^>]*href)=?>?[^<]*#[^<\"]*", sitemap)
    hashed = re.findall(r'(?:<loc>|href=")([^"<]*#[^"<]*)', sitemap)
    if hashed:
        rep.fail("sitemap.xml zawiera URL-e z fragmentami: %s" % hashed[:5])
        bad = True
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    expected = len(sitemap_slugs()) + 5
    if len(locs) != expected:
        rep.fail("sitemap.xml: %d URL-i (oczekiwano %d)" % (len(locs), expected))
        bad = True
    else:
        rep.ok("sitemap.xml — %d URL-i, bez fragmentow" % len(locs))
    expected_locs = [LANG_URL[l] for l in LANGS] + \
                    ["%s/%s/" % (SITE, slug) for slug, _p in sitemap_slugs()]
    if locs and locs != expected_locs:
        rep.fail("sitemap.xml: nieoczekiwana lista URL-i")
        bad = True
    if not bad:
        rep.ok("hreflang na stronach jezykowych — bez fragmentow #pl/#en")


def check_extras(rep):
    rep.head("9. Kontrole dodatkowe (audio, JS, robots, 404, przelacznik jezyka)")
    dead = [
        "7.-20-marca-2021a_NN-",
        "8.-20-marca-2021b_NN-",
        "AUDIO-2021-09-30-11-49-07-NN-opowiada",
        "9.-Lara-tel-do-mnie-Jareniowki",
    ]
    hits = Counter()
    for path, _lang in PAGES:
        raw, _soup = load(path)
        for needle in dead:
            if needle in raw:
                hits[needle] += 1
    if hits:
        for needle, count in hits.items():
            rep.fail("martwy link audio nadal obecny (%d stron): %s" % (count, needle))
    else:
        rep.ok("brak martwych linkow audio na wszystkich %d stronach" % len(PAGES))

    for path, _lang in PAGES:
        raw, soup = load(path)
        problems = []
        if "btn.addEventListener('click', () => setLanguage(" in raw:
            problems.append("pozostal nasluch przelacznika jezyka")
        if "if (langMap[hashLang]) setLanguage(hashLang);" in raw:
            problems.append("pozostalo ustawianie jezyka z hasha")
        if "location.replace(m[h])" not in raw:
            problems.append("brak przekierowania starych linkow hashowych")
        if "header.classList.toggle('scrolled'" in raw and \
                "if (header) header.classList.toggle('scrolled'" not in raw:
            problems.append("brak straznika null dla naglowka")
        if "if (mobileMenuBtn && navLinks)" not in raw:
            problems.append("brak straznika null dla menu mobilnego")
        switcher = soup.find("div", class_="lang-switcher")
        anchors = switcher.find_all("a", class_="lang-btn") if switcher else []
        if len(anchors) != 5:
            problems.append("przelacznik jezyka: %d linkow" % len(anchors))
        active = [a for a in anchors if "active" in (a.get("class") or [])]
        if len(active) != 1:
            problems.append("przelacznik jezyka: %d aktywnych" % len(active))
        if "visitor-count.json" in raw and BASE + "/visitor-count.json" not in raw:
            problems.append("wzgledna sciezka visitor-count.json w JS")
        if problems:
            rep.fail("%s: %s" % (path, "; ".join(problems)))
    if rep.lines[-1].startswith("  BLAD") is False:
        rep.ok("JavaScript i przelacznik jezyka — poprawne na wszystkich stronach")

    with open(os.path.join(ROOT, "robots.txt"), encoding="utf-8") as fh:
        robots = fh.read()
    if "Sitemap: %s/sitemap.xml" % SITE not in robots:
        rep.fail("robots.txt bez wpisu Sitemap")
    elif re.search(r"^\s*Disallow:\s*/\S", robots, re.M):
        rep.fail("robots.txt blokuje sciezki (np. /docs/)")
    else:
        rep.ok("robots.txt — Sitemap obecny, nic nie blokuje /docs/")

    raw, soup = load("404.html")
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    if not robots_meta or "noindex" not in robots_meta.get("content", ""):
        rep.fail("404.html bez meta robots=noindex")
    else:
        links = {a["href"] for a in soup.find_all("a", href=True)}
        needed = {BASE + "/" + s["slug"] + "/" for s in CONTENT_PAGES} | \
                 {BASE + "/" + h["slug"] + "/" for h in HUBS} | {BASE + "/"}
        if not needed.issubset(links):
            rep.fail("404.html: brak linkow do %s" % sorted(needed - links))
        else:
            rep.ok("404.html — noindex, linki do strony glownej, hubów i podstron")

    for path, _lang in PAGES:
        raw, soup = load(path)
        if soup.find("base") is not None:
            rep.fail("%s: znaleziono tag <base>" % path)


def check_navigation(rep):
    """10. Menu: dokladnie szesc klikalnych zakladek, zaden drugi rzad."""
    rep.head("10. Nawigacja — dokladnie 6 zakladek, kazda klikalna, jeden rzad")
    expected_keys = [key for key, _href, _labels in NAV_TABS]
    for path, lang in PAGES:
        raw, soup = load(path)
        nav = soup.find("nav", id="nav-links")
        problems = []
        if nav is None:
            problems.append("brak nav#nav-links")
        else:
            links = nav.find_all("a", recursive=False)
            if len(links) != 6:
                problems.append("%d zakladek (oczekiwano 6)" % len(links))
            if [a.get("data-nav") for a in links] != expected_keys:
                problems.append("inna kolejnosc/zestaw zakladek")
            for a in links:
                href = (a.get("href") or "").strip()
                if not href or href.startswith("#"):
                    problems.append("zakladka bez wlasnego adresu: %r" % href)
                label = a.get_text(" ", strip=True)
                for forbidden in ("Blocki cyngiel", "maszynowe recenzje",
                                  "Nagranie ", "List otwarty"):
                    if forbidden.lower() in label.lower():
                        problems.append("zabroniona etykieta menu: %s" % label)
        if soup.find("nav", class_="sub-nav") is not None:
            problems.append("pozostal drugi rzad zakladek (nav.sub-nav)")
        if "nav.classList.contains('open')" not in raw:
            problems.append("brak obslugi Escape dla menu mobilnego")
        if problems:
            rep.fail("%s: %s" % (path, "; ".join(problems)))
    if not rep.lines[-1].startswith("  BLAD"):
        rep.ok("menu — 6 klikalnych zakladek na wszystkich %d stronach, "
               "bez drugiego rzedu" % len(PAGES))


def check_headings(rep):
    """11. Hierarchia naglowkow: dokladnie jeden H1 na stronie."""
    rep.head("11. Hierarchia naglowkow (jeden H1 na stronie)")
    bad = 0
    for path, _lang in PAGES:
        raw, soup = load(path)
        h1 = soup.find_all("h1")
        if len(h1) != 1:
            rep.fail("%s: %d naglowkow H1" % (path, len(h1)))
            bad += 1
    if not bad:
        rep.ok("kazda z %d stron ma dokladnie jeden H1" % len(PAGES))


def check_recordings(rep):
    """12. Podstrony nagran: metryczka, nota o numeracji, poprzednie/nastepne."""
    rep.head("12. Podstrony nagran (metryczka, numeracja, nawigacja)")
    for rec in RECORDINGS:
        path = "%s/index.html" % rec["slug"]
        raw, soup = load(path)
        problems = []
        if soup.find("ul", class_="rec-meta") is None:
            problems.append("brak metryczki (data/uczestnicy/czas)")
        if "errata-numeracja-nagran" not in raw:
            problems.append("brak linku do noty o numeracji")
        nav = soup.find("nav", class_="rec-prevnext")
        if nav is None:
            problems.append("brak nawigacji poprzednie/nastepne")
        for audio in soup.find_all("audio"):
            if audio.has_attr("autoplay"):
                problems.append("odtwarzacz z autoplay")
        if problems:
            rep.fail("%s: %s" % (path, "; ".join(problems)))
        else:
            rep.ok("%s — metryczka, nota o numeracji, nawigacja, bez autoplay" % path)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(ROOT), "verify-report.txt")
    rep = Report()
    rep.lines.append("RAPORT WERYFIKACJI — KorupcjaNCN, Pakiet B")
    rep.lines.append("Katalog: %s" % ROOT)
    rep.lines.append("Stron sprawdzanych: %d (5 jezykowych + %d hubow + %d podstron "
                     "tresci + %d nagran + 5 skorowidzow) + 404.html"
                     % (len(PAGES), len(HUBS), len(CONTENT_PAGES), len(RECORDINGS)))

    check_parsing_and_ids(rep)
    check_head_uniqueness(rep)
    check_single_language(rep)
    check_local_links(rep)
    check_anchors(rep)
    check_sizes(rep)
    check_hreflang(rep)
    check_no_hash_leftovers(rep)
    check_extras(rep)
    check_navigation(rep)
    check_headings(rep)
    check_recordings(rep)

    rep.head("PODSUMOWANIE")
    if rep.errors:
        rep.lines.append("  BLEDY: %d — raport NIE jest czysty" % rep.errors)
    else:
        rep.lines.append("  Bledow: 0 — raport czysty.")

    text = rep.text()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    sys.stdout.write(text)
    print("Raport zapisany do: %s" % out)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
