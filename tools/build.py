#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator stron statycznych KorupcjaNCN (Pakiet B).

Zrodlo prawdy: src/index.src.html (5 jezykow w jednym pliku, bloki .lang-block).
Skrypt generuje:
  * index.html                      — PL (hub, skroty wydzielonych sekcji)
  * en/ fr/ de/ uk/ index.html      — pelna tresc w danym jezyku
  * 8 stron sekcyjnych PL           — pelna tresc jednej sekcji
  * sitemap.xml, 404.html

Uruchomienie: python3 tools/build.py
Wymagania: Python 3 + beautifulsoup4 (parser html.parser — bez lxml).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from collections import Counter

from bs4 import BeautifulSoup, Comment

# --------------------------------------------------------------------------
# Konfiguracja
# --------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "index.src.html")

BASE = "/KorupcjaNCN"
SITE = "https://ludvigboltzmann.github.io/KorupcjaNCN"
BUILD_DATE = "2026-07-30"
PUBLISHED = "2026-03-03"

LANGS = ["pl", "en", "fr", "de", "uk"]

HTML_LANG = {"pl": "pl", "en": "en", "fr": "fr", "de": "de", "uk": "uk"}
OG_LOCALE = {"pl": "pl_PL", "en": "en_US", "fr": "fr_FR", "de": "de_DE", "uk": "uk_UA"}
LANG_BTN = {
    "pl": ("PL", "Polski"),
    "en": ("EN", "English"),
    "fr": ("FR", "Français"),
    "de": ("DE", "Deutsch"),
    "uk": ("UA", "Українська"),
}
LANG_PATH = {
    "pl": BASE + "/",
    "en": BASE + "/en/",
    "fr": BASE + "/fr/",
    "de": BASE + "/de/",
    "uk": BASE + "/uk/",
}
LANG_URL = {k: SITE + v[len(BASE):] for k, v in LANG_PATH.items()}

# title / description stron jezykowych (punkt 5 specyfikacji)
LANG_META = {
    "pl": (
        "Korupcja w Narodowym Centrum Nauki (NCN) — dowody sygnalisty | Dr Witold Kilarski",
        "Archiwum dowodów sygnalisty: nagrania, dokumenty i wyroki w sprawie domniemanej "
        "korupcji w Narodowym Centrum Nauki. Sprawa dr. Witolda Kilarskiego, dyrektora NCN "
        "Zbigniewa Błockiego i grantu NAWA Polskie Powroty.",
    ),
    "en": (
        "Corruption at Poland's National Science Centre (NCN) — a whistleblower's evidence "
        "| Dr Witold Kilarski",
        "Whistleblower evidence archive: audio recordings, documents and court rulings on "
        "alleged corruption at Poland's National Science Centre (NCN). The case of Dr Witold "
        "Kilarski, NCN director Zbigniew Błocki and the NAWA Polish Returns grant.",
    ),
    "fr": (
        "Corruption au Centre national des sciences de Pologne (NCN) — les preuves d'un "
        "lanceur d'alerte | Dr Witold Kilarski",
        "Archives d'un lanceur d'alerte : enregistrements, documents et décisions de justice "
        "sur la corruption présumée au Centre national des sciences de Pologne (NCN). "
        "L'affaire du Dr Witold Kilarski et du directeur du NCN Zbigniew Błocki.",
    ),
    "de": (
        "Korruption am Nationalen Wissenschaftszentrum Polens (NCN) — Beweise eines "
        "Whistleblowers | Dr Witold Kilarski",
        "Beweisarchiv eines Whistleblowers: Tonaufnahmen, Dokumente und Gerichtsurteile zur "
        "mutmaßlichen Korruption am Nationalen Wissenschaftszentrum Polens (NCN). Der Fall "
        "Dr. Witold Kilarski und NCN-Direktor Zbigniew Błocki.",
    ),
    "uk": (
        "Корупція в Національному науковому центрі Польщі (NCN) — докази викривача "
        "| Dr Witold Kilarski",
        "Архів доказів викривача: аудіозаписи, документи та судові рішення щодо ймовірної "
        "корупції в Національному науковому центрі Польщі (NCN). Справа д-ра Вітольда "
        "Кіларського та директора NCN Збігнєва Блоцького.",
    ),
}

# Wydzielane sekcje PL (punkt 5 i 7 specyfikacji)
SECTIONS = [
    {
        "slug": "sprawa-komornika",
        "id": "komornik",
        "short": "Sprawa komornicza Km 834/26",
        "title": "Sprawa komornicza Km 834/26 — zajęcie konta dziecka i konta wspólnego "
                 "| Dr Witold Kilarski",
        "desc": "Egzekucja Km 834/26 bez doręczenia tytułu wykonawczego: zajęcie wspólnego "
                "rachunku małżeńskiego i konta 12-letniego dziecka (eKonto JUNIOR), "
                "ok. 74 425 zł zadłużenia, komornik Krzysztof Przybyła, mBank.",
    },
    {
        "slug": "wyrok-kafkowski",
        "id": "wyrok-kafkowski",
        "short": "Wyrok kafkowski (I C 1671/22)",
        "title": "Sprawa I C 1671/22 — apelacja odrzucona bez wiedzy strony "
                 "| Dr Witold Kilarski",
        "desc": "Analiza postępowania I C 1671/22: apelacja odrzucona bez wiedzy powoda, "
                "przebieg doręczeń, reakcja sądu i konsekwencje egzekucyjne w sprawie "
                "sygnalisty NCN.",
    },
    {
        "slug": "bezczynnosc-uj",
        "id": "uj-inaction",
        "short": "Bezczynność Uniwersytetu Jagiellońskiego",
        "title": "Bezczynność Uniwersytetu Jagiellońskiego (marzec–lipiec 2026) "
                 "| Dr Witold Kilarski",
        "desc": "Chronologia korespondencji z Uniwersytetem Jagiellońskim w sprawie "
                "domniemanych powiązań Błocki–Liana i braku reakcji uczelni na zgłoszenia "
                "sygnalisty, marzec–lipiec 2026.",
    },
    {
        "slug": "blocki-babik-liana",
        "id": "sprawa-blocki-babik-liana",
        "short": "Błocki, Babik, Liana",
        "title": "Sprawa: Zbigniew Błocki, Babik, Liana — postępowanie przeciwko byłemu "
                 "dyrektorowi NCN | Dr Witold Kilarski",
        "desc": "Dokumentacja sprawy przeciwko byłemu dyrektorowi Narodowego Centrum Nauki "
                "Zbigniewowi Błockiemu oraz domniemanych powiązań personalnych "
                "Błocki–Babik–Liana na Uniwersytecie Jagiellońskim.",
    },
    {
        "slug": "maszynowe-recenzje-ncn",
        "id": "mudelsee",
        "short": "Maszynowe recenzje NCN (sprawa Mudelsee)",
        "title": "NCN i maszynowe recenzje — sprawa Mudelsee (kopiowane recenzje grantowe) "
                 "| Dr Witold Kilarski",
        "desc": "Dowody na seryjne, maszynowo generowane recenzje wniosków grantowych "
                "w Narodowym Centrum Nauki (sprawa Mudelsee) i brak reakcji NCN na "
                "zgłoszenie nieprawidłowości.",
    },
    {
        "slug": "dokumenty",
        "id": "documents",
        "short": "Dokumenty i dowody",
        "title": "Dokumenty i dowody — korupcja w NCN | Dr Witold Kilarski",
        "desc": "Pełne archiwum dokumentów: e-maile NCN, pisma procesowe, decyzje "
                "prokuratury, wyroki, korespondencja z NAWA, WUM i Uniwersytetem "
                "Jagiellońskim. Wszystkie pliki do pobrania.",
    },
    {
        "slug": "sprawy-sadowe",
        "id": "courts",
        "short": "Sprawy sądowe sygnalisty",
        "title": "Sprawy sądowe sygnalisty — zniesławienie, apelacje, ETPC "
                 "| Dr Witold Kilarski",
        "desc": "Wykaz postępowań sądowych przeciwko sygnaliście NCN: proces o zniesławienie "
                "wytoczony przez dyrektora NCN, sprawy cywilne, apelacje i skarga do "
                "Europejskiego Trybunału Praw Człowieka.",
    },
    {
        "slug": "prokuratura",
        "id": "prokuratura-ochonska",
        "short": "Odmowa śledztwa przez prokuraturę",
        "title": "Odmowa wszczęcia śledztwa przez prokuraturę — sprawa NCN "
                 "| Dr Witold Kilarski",
        "desc": "Pełne pisma i postanowienia: odmowa wszczęcia śledztwa w sprawie "
                "domniemanej korupcji w Narodowym Centrum Nauki, zażalenia i argumentacja "
                "prawna sygnalisty.",
    },
]

SECTION_BY_ID = {s["id"]: s for s in SECTIONS}

# Naprawa martwych linkow audio (punkt 8 specyfikacji)
AUDIO_RENAMES = [
    (
        "docs/7.-20-marca-2021a_NN-2021_03_20_13_04_17.mp3",
        "docs/7.-20-marca-2021a_LBM-2021_03_20_13_04_17.mp3",
    ),
    (
        "docs/8.-20-marca-2021b_NN-2021_03_20_14_20_24.mp3",
        "docs/8.-20-marca-2021b_LBM-2021_03_20_14_20_24.mp3",
    ),
    (
        "docs/10.-AUDIO-2021-09-30-11-49-07-NN-opowiada-jaki-mogl-byc-mechanizm-"
        "zniszczenia-WItka-przez-Blockiego-i-Draga_sss.mp3",
        "docs/10.-AUDIO-2021-09-30-11-49-07-Laura-opowiada-jaki-mogl-byc-mechanizm-"
        "zniszczenia-WItka-przez-Blockiego-i-Draga_sss.mp3",
    ),
]

MISSING_AUDIO = "docs/9.-Lara-tel-do-mnie-Jareniowki_AUD-20231216-WA0001.m4a"
MISSING_AUDIO_NOTE = {
    "pl": "Plik audio tego nagrania jest chwilowo niedostępny — zostanie ponownie opublikowany.",
    "en": "The audio file for this recording is temporarily unavailable and will be republished.",
    "fr": "Le fichier audio de cet enregistrement est temporairement indisponible et sera republié.",
    "de": "Die Audiodatei dieser Aufnahme ist derzeit nicht verfügbar und wird erneut veröffentlicht.",
    "uk": "Аудіофайл цього запису тимчасово недоступний і буде опублікований повторно.",
}

NAV_LANG_CLASSES = {"nav-" + l for l in LANGS}

EXTRA_CSS = """
/* ============================================================
   Pakiet B (2026-07-30): przelacznik jezyka jako linki, breadcrumb,
   CTA skrotu sekcji, blok "Powiazane sekcje", notka o braku audio.
   ============================================================ */
.lang-switcher a.lang-btn{text-decoration:none;display:inline-block;}
.breadcrumb{margin:var(--space-6) 0 var(--space-4);font-size:var(--text-sm);color:var(--color-text-muted);text-align:left;}
.breadcrumb a{color:var(--color-text-muted);}
.breadcrumb a:hover{color:var(--color-accent);}
.section-cta{margin-top:var(--space-6);}
.section-cta a{font-weight:700;color:var(--color-accent);}
.related-pages{margin:var(--space-12) 0 var(--space-8);padding-top:var(--space-6);border-top:1px solid var(--color-border);}
.related-pages h2{font-size:var(--text-lg);margin:0 0 var(--space-4);}
.related-pages ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:var(--space-3);justify-content:center;}
.related-pages li{margin:0;}
.related-pages a{display:inline-block;padding:var(--space-2) var(--space-4);border:1px solid var(--color-border);border-radius:6px;font-size:var(--text-sm);text-decoration:none;color:var(--color-link);}
.related-pages a:hover{border-color:var(--color-accent);color:var(--color-accent);}
.audio-unavailable{margin:var(--space-4) 0;padding:var(--space-4);border:1px dashed var(--color-border-strong);border-radius:6px;background:var(--color-surface);font-size:var(--text-sm);color:var(--color-text-muted);}
"""

HASH_REDIRECT_JS = """
(function(){
  var m = {en:'/KorupcjaNCN/en/', fr:'/KorupcjaNCN/fr/', de:'/KorupcjaNCN/de/', uk:'/KorupcjaNCN/uk/', pl:'/KorupcjaNCN/'};
  var h = location.hash.replace('#','');
  if (m[h] && location.pathname.replace(/index\\.html$/,'') !== m[h]) { location.replace(m[h]); }
})();
"""


class BuildError(RuntimeError):
    pass


def expect(condition, message):
    if not condition:
        raise BuildError(message)


# --------------------------------------------------------------------------
# Wczytanie i naprawa zrodla (poprawki tekstowe wspolne dla wszystkich stron)
# --------------------------------------------------------------------------

def load_source():
    with open(SRC, encoding="utf-8") as fh:
        raw = fh.read()

    for old, new in AUDIO_RENAMES:
        expect(old in raw, "brak w zrodle sciezki audio do naprawy: %s" % old)
        raw = raw.replace(old, new)

    # Data ostatniej modyfikacji (OG + JSON-LD).
    raw, n = re.subn(
        r'(<meta property="article:modified_time" content=")[^"]*(")',
        r"\g<1>%s\g<2>" % BUILD_DATE, raw)
    expect(n == 1, "nie znaleziono article:modified_time")
    raw, n = re.subn(r'("dateModified":\s*")[^"]*(")', r"\g<1>%s\g<2>" % BUILD_DATE, raw)
    expect(n >= 1, "nie znaleziono dateModified w JSON-LD")

    return raw


def replace_missing_audio(soup):
    """Punkt 8: nieistniejacy plik 9 -> notka w ramce (per jezyk)."""
    sources = soup.select('source[src="%s"]' % MISSING_AUDIO)
    expect(len(sources) == 5, "oczekiwano 5 odwolan do brakujacego pliku 9, jest %d" % len(sources))
    for src in list(sources):
        audio = src.find_parent("audio")
        expect(audio is not None, "source pliku 9 bez elementu <audio>")
        block = src.find_parent(attrs={"data-lang": True})
        lang = block.get("data-lang") if block else "pl"
        note = soup.new_tag("div", attrs={
            "class": "audio-unavailable",
            "role": "note",
            "aria-label": "Audio unavailable",
        })
        note.string = MISSING_AUDIO_NOTE[lang]
        audio.replace_with(note)
        note.insert_before(Comment(" TODO: wgrac plik 9 "))


# --------------------------------------------------------------------------
# Filtrowanie jezyka
# --------------------------------------------------------------------------

def is_anchor_only(tag):
    """Pusty element z id — kotwica przewijania, niezalezna od jezyka."""
    return bool(tag.get("id")) and not tag.find(True) and not tag.get_text(strip=True)


def filter_language(soup, lang):
    salvaged = []
    for block in soup.find_all("div", attrs={"data-lang": True}):
        classes = block.get("class") or []
        if "lang-block" not in classes:
            continue
        if block.get("data-lang") != lang:
            for anchor in block.find_all(is_anchor_only):
                block.insert_before(anchor.extract())
                salvaged.append(anchor)
            block.decompose()
        else:
            block["class"] = ["lang-block", "active"]

    counts = Counter(t["id"] for t in soup.find_all(attrs={"id": True}))
    for anchor in salvaged:
        if counts[anchor["id"]] > 1:
            counts[anchor["id"]] -= 1
            anchor.decompose()

    for tag in soup.find_all("script", attrs={"data-lang": True}):
        tag["data-lang"] = lang

    for tag in soup.find_all(True):
        classes = tag.get("class") or []
        hit = NAV_LANG_CLASSES.intersection(classes)
        if not hit:
            continue
        if "nav-" + lang in hit:
            if tag.get("style") == "display:none":
                del tag["style"]
        else:
            tag.decompose()

    soup.html["lang"] = HTML_LANG[lang]
    return soup


# --------------------------------------------------------------------------
# Przelacznik jezyka -> prawdziwe linki
# --------------------------------------------------------------------------

def rewrite_lang_switcher(soup, active_lang):
    switcher = soup.find("div", class_="lang-switcher")
    expect(switcher is not None, "nie znaleziono .lang-switcher")
    switcher.clear()
    for lang in LANGS:
        label, aria = LANG_BTN[lang]
        classes = ["lang-btn", "active"] if lang == active_lang else ["lang-btn"]
        a = soup.new_tag("a", href=LANG_PATH[lang])
        a["class"] = classes
        a["hreflang"] = lang
        a["aria-label"] = aria
        a.string = label
        switcher.append(a)


# --------------------------------------------------------------------------
# JavaScript
# --------------------------------------------------------------------------

def transform_scripts(soup):
    hits = {"lang_click": 0, "hash_lang": 0, "header_guard": 0,
            "header_height": 0, "menu_guard": 0, "cv_guard": 0}

    for script in soup.find_all("script"):
        if script.get("src"):
            continue
        code = script.string
        if not code:
            continue
        new = code

        # Nasluchy przelacznika jezyka (przelacznik jest teraz zestawem linkow).
        new, n = re.subn(
            r"\n[ \t]*langBtns\.forEach\(btn => \{\n[ \t]*btn\.addEventListener\('click',"
            r" \(\) => setLanguage\(btn\.dataset\.lang\)\);\n[ \t]*\}\);",
            "", new)
        hits["lang_click"] += n

        # Ustawianie jezyka z hasha (zastapione przekierowaniem w <head>).
        new, n = re.subn(
            r"\n[ \t]*// Check hash for language on load\n"
            r"[ \t]*const hashLang = window\.location\.hash\.replace\('#', ''\);\n"
            r"[ \t]*if \(langMap\[hashLang\]\) setLanguage\(hashLang\);",
            "", new)
        hits["hash_lang"] += n

        # Straznik null dla naglowka.
        new, n = re.subn(
            r"\n([ \t]*)header\.classList\.toggle\('scrolled', scrollY > 20\);",
            r"\n\1if (header) header.classList.toggle('scrolled', scrollY > 20);", new)
        hits["header_guard"] += n

        new, n = re.subn(
            r"const headerHeight = header\.offsetHeight;",
            "const headerHeight = header ? header.offsetHeight : 0;", new)
        hits["header_height"] += n

        # Straznik null dla menu mobilnego (przycisk + lista linkow).
        match = re.search(
            r"([ \t]*mobileMenuBtn\.addEventListener\('click'.*?\n[ \t]*\}\);\n"
            r"[ \t]*// Close mobile menu when nav link is clicked\n"
            r"[ \t]*navLinks\.querySelectorAll.*?\n[ \t]*\}\);\n)",
            new, re.S)
        if match:
            new = (new[:match.start()]
                   + "  if (mobileMenuBtn && navLinks) {\n"
                   + match.group(1)
                   + "  }\n"
                   + new[match.end():])
            hits["menu_guard"] += 1

        # Straznik null dla przegladarki CV (moze nie byc na stronach sekcyjnych).
        new, n = re.subn(
            r"(\n[ \t]*var totalPages = pages\.length;)",
            r"\1\n    if (!pages.length || !prevBtn || !nextBtn || !indicator) return;", new)
        hits["cv_guard"] += n

        if new != code:
            script.string = new

    for key, expected in (("lang_click", 1), ("hash_lang", 1), ("header_guard", 1),
                          ("header_height", 1), ("menu_guard", 1), ("cv_guard", 1)):
        expect(hits[key] == expected,
               "transformacja JS '%s': oczekiwano %d trafien, jest %d"
               % (key, expected, hits[key]))

    # Przekierowanie starych linkow hashowych — jako pierwszy skrypt w <head>,
    # aby wykonac sie przed renderowaniem strony.
    redirect = soup.new_tag("script")
    redirect.string = HASH_REDIRECT_JS
    anchor = soup.head.find("meta", attrs={"name": "viewport"})
    if anchor is not None:
        anchor.insert_after(redirect)
    else:
        soup.head.insert(0, redirect)

    # Licznik odwiedzin: sciezka wzgledna w JS -> sciezka absolutna.
    fixed = 0
    for script in soup.find_all("script"):
        if script.get("src") or not script.string:
            continue
        if "REPO_FALLBACK = 'visitor-count.json'" in script.string:
            script.string = script.string.replace(
                "REPO_FALLBACK = 'visitor-count.json'",
                "REPO_FALLBACK = '%s/visitor-count.json'" % BASE)
            fixed += 1
    expect(fixed == 1, "nie znaleziono sciezki visitor-count.json w JS")


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------

def append_css(soup):
    styles = soup.find_all("style")
    expect(bool(styles), "brak bloku <style> w zrodle")
    target = max(styles, key=lambda s: len(s.string or ""))
    target.string = (target.string or "") + EXTRA_CSS


# --------------------------------------------------------------------------
# Metadane <head>
# --------------------------------------------------------------------------

def set_meta_content(soup, attr, key, value):
    tag = soup.head.find("meta", attrs={attr: key})
    expect(tag is not None, "brak meta %s=%s" % (attr, key))
    tag["content"] = value


def set_head(soup, *, lang, title, description, page_url, hreflang_cluster, keep_faq):
    head = soup.head

    expect(soup.title is not None, "brak <title>")
    soup.title.string = title

    set_meta_content(soup, "name", "description", description)
    set_meta_content(soup, "property", "og:title", title)
    set_meta_content(soup, "property", "og:description", description)
    set_meta_content(soup, "property", "og:url", page_url)
    set_meta_content(soup, "property", "og:locale", OG_LOCALE[lang])
    set_meta_content(soup, "name", "twitter:title", title)
    set_meta_content(soup, "name", "twitter:description", description)

    # keywords: ~90 fraz w zrodle — usuwamy calkowicie (wariant preferowany).
    for tag in head.find_all("meta", attrs={"name": "keywords"}):
        tag.decompose()

    # og:locale:alternate — tylko na stronach jezykowych.
    for tag in head.find_all("meta", attrs={"property": "og:locale:alternate"}):
        tag.decompose()
    if hreflang_cluster:
        anchor = head.find("meta", attrs={"property": "og:locale"})
        for other in LANGS:
            if other == lang:
                continue
            tag = soup.new_tag("meta")
            tag["property"] = "og:locale:alternate"
            tag["content"] = OG_LOCALE[other]
            anchor.insert_after(tag)
            anchor = tag

    # Jezyk dokumentu w metadanych pomocniczych.
    lang_meta = head.find("meta", attrs={"http-equiv": "content-language"})
    if lang_meta is not None:
        lang_meta["content"] = HTML_LANG[lang]
    dc_lang = head.find("meta", attrs={"name": "DC.language"})
    if dc_lang is not None:
        dc_lang["content"] = HTML_LANG[lang]

    # canonical
    canonical = head.find("link", attrs={"rel": ["canonical"]})
    expect(canonical is not None, "brak link[rel=canonical]")
    canonical["href"] = page_url

    # hreflang — usun stare wpisy z fragmentami, dodaj poprawny klaster.
    for tag in head.find_all("link", attrs={"rel": ["alternate"]}):
        tag.decompose()
    if hreflang_cluster:
        anchor = canonical
        for other in LANGS + ["x-default"]:
            href = LANG_URL["pl"] if other == "x-default" else LANG_URL[other]
            tag = soup.new_tag("link", href=href)
            tag["rel"] = "alternate"
            tag["hreflang"] = other
            anchor.insert_after(tag)
            anchor = tag

    if not keep_faq:
        for script in head.find_all("script", attrs={"type": "application/ld+json"}):
            data = json.loads(script.string)
            if data.get("@type") == "FAQPage":
                script.decompose()


# --------------------------------------------------------------------------
# JSON-LD
# --------------------------------------------------------------------------

def ld_scripts(soup):
    return [s for s in soup.find_all("script", attrs={"type": "application/ld+json"})]


def dump_ld(script, data):
    script.string = "\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def update_graph_for_language(soup, lang, page_url, id_to_url):
    for script in ld_scripts(soup):
        data = json.loads(script.string)
        graph = data.get("@graph")
        if not graph:
            continue
        for node in graph:
            ntype = node.get("@type")
            if ntype == "Article":
                node["headline"] = LANG_META[lang][0]
                node["description"] = LANG_META[lang][1]
                node["inLanguage"] = HTML_LANG[lang]
                node["dateModified"] = BUILD_DATE
                node["mainEntityOfPage"] = page_url
            elif ntype == "BreadcrumbList":
                for item in node.get("itemListElement", []):
                    url = item.get("item", "")
                    if not url.startswith(SITE):
                        continue
                    frag = url.split("#", 1)[1] if "#" in url else ""
                    if frag and frag in id_to_url:
                        item["item"] = id_to_url[frag]
                    elif frag:
                        item["item"] = page_url + "#" + frag
                    else:
                        item["item"] = page_url
        dump_ld(script, data)


def section_ld(section, headline):
    page_url = SITE + "/" + section["slug"] + "/"
    person = {"@type": "Person", "name": "Dr Witold Kilarski"}
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": headline,
                "description": section["desc"],
                "inLanguage": "pl",
                "datePublished": PUBLISHED,
                "dateModified": BUILD_DATE,
                "author": person,
                "publisher": person,
                "mainEntityOfPage": page_url,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Strona główna",
                     "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": section["short"],
                     "item": page_url},
                ],
            },
        ],
    }


# --------------------------------------------------------------------------
# Sciezki zasobow -> absolutne od korzenia serwera
# --------------------------------------------------------------------------

ASSET_ATTRS = ("href", "src", "poster", "data-src")
SKIP_PREFIXES = ("http://", "https://", "//", "#", "mailto:", "tel:", "javascript:",
                 "data:", "/")


def absolutize_assets(soup):
    for tag in soup.find_all(True):
        for attr in ASSET_ATTRS:
            value = tag.get(attr)
            if not isinstance(value, str):
                continue
            value = value.strip()
            if not value or value.startswith(SKIP_PREFIXES):
                continue
            tag[attr] = BASE + "/" + value.lstrip("./")


# --------------------------------------------------------------------------
# Kotwice
# --------------------------------------------------------------------------

# `#top` nie ma odpowiadajacego id — przegladarki traktuja go jako "gora strony"
# zgodnie z HTML5 (podobnie jak puste `#`). Zostawiamy bez zmian.
NATIVE_FRAGMENTS = {"", "top"}


def page_ids(soup):
    return {t["id"] for t in soup.find_all(attrs={"id": True})}


def rewrite_anchors(soup, *, id_to_url, always_remap=False):
    """Kotwice bez celu na tej stronie -> pelne sciezki do stron docelowych.

    `always_remap` (strona glowna PL): linki do wydzielonych sekcji prowadza do
    ich nowych URL-i, mimo ze skrocona sekcja o tym samym `id` nadal istnieje —
    `id` zostaje wylacznie dla starych, zewnetrznych odnosnikow.
    """
    ids = page_ids(soup)
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href.startswith("#"):
            continue
        frag = href[1:]
        if frag in NATIVE_FRAGMENTS:
            continue
        target = id_to_url.get(frag)
        if target and (always_remap or frag not in ids):
            a["href"] = target
        elif frag not in ids:
            a["href"] = BASE + "/#" + frag


# --------------------------------------------------------------------------
# Skroty sekcji na stronie glownej PL
# --------------------------------------------------------------------------

SUMMARY_KEEP_CLASSES = {"highlight-box", "komornik-callout", "nn-definition", "intro",
                        "section-label"}
SUMMARY_MAX_CHARS = 2000
SUMMARY_MAX_BLOCKS = 3


def prune_to_chain(section, keep):
    """Usuwa z sekcji wszystko poza lancuchem przodkow elementu `keep`."""
    node = keep
    while node is not section:
        parent = node.parent
        for sibling in list(parent.find_all(recursive=False)):
            if sibling is not node:
                sibling.decompose()
        node = parent


def build_summary(soup, section_tag, section):
    block = section_tag.find("div", class_="lang-block")
    expect(block is not None, "sekcja %s bez bloku jezykowego" % section["id"])

    label = None
    heading = None
    kept = []
    chars = 0

    children = block.find_all(recursive=False)
    for child in children:
        classes = set(child.get("class") or [])
        if heading is None:
            if "section-label" in classes:
                label = child
                continue
            if child.name == "h2":
                heading = child
                continue
            continue
        if child.name == "p" or classes.intersection(SUMMARY_KEEP_CLASSES - {"section-label"}):
            kept.append(child)
            chars += len(child.get_text(" ", strip=True))
            if len(kept) >= SUMMARY_MAX_BLOCKS or chars >= SUMMARY_MAX_CHARS:
                break
            continue
        break

    expect(heading is not None, "sekcja %s bez <h2>" % section["id"])
    expect(bool(kept), "sekcja %s: nie udalo sie zbudowac skrotu" % section["id"])

    headline = heading.get_text(" ", strip=True)

    keep_nodes = ([label] if label is not None else []) + [heading] + kept
    for node in keep_nodes:
        node.extract()

    prune_to_chain(section_tag, block)
    block.clear()
    for node in keep_nodes:
        block.append(node)

    cta = soup.new_tag("p")
    cta["class"] = ["section-cta"]
    link = soup.new_tag("a", href=BASE + "/" + section["slug"] + "/")
    link.string = "Czytaj pełną analizę: %s →" % section["short"]
    cta.append(link)
    block.append(cta)

    return headline


# --------------------------------------------------------------------------
# Elementy nawigacyjne stron sekcyjnych
# --------------------------------------------------------------------------

def build_breadcrumb(soup, section):
    nav = soup.new_tag("nav")
    nav["class"] = ["breadcrumb"]
    nav["aria-label"] = "Breadcrumb"
    home = soup.new_tag("a", href=BASE + "/")
    home.string = "Strona główna"
    nav.append(home)
    nav.append(" › ")
    current = soup.new_tag("span")
    current.string = section["short"]
    nav.append(current)
    return nav


def build_related(soup, current_slug):
    nav = soup.new_tag("nav")
    nav["class"] = ["related-pages"]
    nav["aria-label"] = "Powiązane sekcje"
    heading = soup.new_tag("h2")
    heading.string = "Powiązane sekcje"
    nav.append(heading)
    ul = soup.new_tag("ul")
    for other in SECTIONS:
        if other["slug"] == current_slug:
            continue
        li = soup.new_tag("li")
        a = soup.new_tag("a", href=BASE + "/" + other["slug"] + "/")
        a.string = other["short"]
        li.append(a)
        ul.append(li)
    li = soup.new_tag("li")
    a = soup.new_tag("a", href=BASE + "/")
    a.string = "Strona główna"
    li.append(a)
    ul.append(li)
    nav.append(ul)
    return nav


# --------------------------------------------------------------------------
# Budowanie stron
# --------------------------------------------------------------------------

def prepared_soup(raw, lang):
    soup = BeautifulSoup(raw, "html.parser")
    replace_missing_audio(soup)
    filter_language(soup, lang)
    return soup


def collect_section_id_map(raw):
    """id -> URL strony, na ktora przeniesiono element (dla kotwic i JSON-LD)."""
    soup = prepared_soup(raw, "pl")
    id_to_url = {}
    for section in SECTIONS:
        tag = soup.find(id=section["id"])
        expect(tag is not None, "brak sekcji #%s w zrodle" % section["id"])
        url = BASE + "/" + section["slug"] + "/"
        for inner in tag.find_all(attrs={"id": True}):
            id_to_url[inner["id"]] = url + "#" + inner["id"]
        id_to_url[section["id"]] = url
    return id_to_url


def finish(soup, path):
    absolutize_assets(soup)
    logo = soup.find("a", class_="header-logo")
    if logo is not None:
        logo["href"] = BASE + "/"
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out) or ROOT, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(str(soup))
    return out


def build_language_page(raw, lang, id_to_url, hub_headlines=None):
    soup = prepared_soup(raw, lang)
    rewrite_lang_switcher(soup, lang)
    transform_scripts(soup)
    append_css(soup)

    title, description = LANG_META[lang]
    page_url = LANG_URL[lang]
    set_head(soup, lang=lang, title=title, description=description, page_url=page_url,
             hreflang_cluster=True, keep_faq=(lang == "pl"))

    if lang == "pl":
        # Skroty wydzielonych sekcji + linki do nowych URL-i.
        for section in SECTIONS:
            tag = soup.find(id=section["id"])
            expect(tag is not None, "brak sekcji #%s" % section["id"])
            headline = build_summary(soup, tag, section)
            if hub_headlines is not None:
                hub_headlines[section["id"]] = headline
        update_graph_for_language(soup, lang, page_url, id_to_url)
        rewrite_anchors(soup, id_to_url=id_to_url, always_remap=True)
    else:
        update_graph_for_language(soup, lang, page_url, {})
        # Strony jezykowe maja pelna tresc — kotwice hashowe zostaja bez zmian.

    path = "index.html" if lang == "pl" else "%s/index.html" % lang
    return finish(soup, path)


def build_section_page(raw, section, id_to_url, headline):
    soup = prepared_soup(raw, "pl")
    rewrite_lang_switcher(soup, "pl")
    transform_scripts(soup)
    append_css(soup)

    page_url = SITE + "/" + section["slug"] + "/"
    set_head(soup, lang="pl", title=section["title"], description=section["desc"],
             page_url=page_url, hreflang_cluster=False, keep_faq=False)

    # Sekcja + nowy <main>: breadcrumb, tresc sekcji, powiazane strony.
    section_tag = soup.find(id=section["id"])
    expect(section_tag is not None, "brak sekcji #%s" % section["id"])
    section_tag.extract()

    main = soup.find("main")
    expect(main is not None, "brak <main>")
    main.clear()
    main.append(build_breadcrumb(soup, section))
    main.append(section_tag)
    main.append(build_related(soup, section["slug"]))

    # Elementy calej witryny, ktorych nie ma na podstronie.
    hero = soup.find("section", class_="hero")
    if hero is not None:
        hero.decompose()
    comments = soup.find(id="comments")
    if comments is not None:
        comments.decompose()
    for stray in soup.find_all("section"):
        if stray is not section_tag and not stray.find_parent("main"):
            stray.decompose()

    # JSON-LD: tylko Article + BreadcrumbList tej podstrony.
    for script in ld_scripts(soup):
        script.decompose()
    ld = soup.new_tag("script", attrs={"type": "application/ld+json"})
    ld.string = "\n" + json.dumps(section_ld(section, headline),
                                 ensure_ascii=False, indent=2) + "\n"
    soup.head.append(ld)

    rewrite_anchors(soup, id_to_url=id_to_url)
    return finish(soup, "%s/index.html" % section["slug"])


# --------------------------------------------------------------------------
# sitemap.xml / 404.html / robots.txt
# --------------------------------------------------------------------------

VIDEO_BLOCK = """    <video:video>
      <video:thumbnail_loc>https://img.youtube.com/vi/Z7DH_iRY78w/maxresdefault.jpg</video:thumbnail_loc>
      <video:title>Korupcja w Narodowym Centrum Nauki (NCN) — Whistleblower documentary</video:title>
      <video:description>Documentary about corruption at Poland's National Science Centre (NCN). Dr Witold Kilarski exposes blackmail, nepotism, and cover-up by NCN Director Zbigniew Błocki.</video:description>
      <video:content_loc>https://www.youtube.com/watch?v=Z7DH_iRY78w</video:content_loc>
      <video:player_loc>https://www.youtube.com/embed/Z7DH_iRY78w</video:player_loc>
      <video:duration>192</video:duration>
      <video:publication_date>2026-03-03</video:publication_date>
      <video:family_friendly>yes</video:family_friendly>
      <video:tag>Narodowe Centrum Nauki</video:tag>
      <video:tag>NCN</video:tag>
      <video:tag>korupcja</video:tag>
      <video:tag>sygnalista</video:tag>
      <video:tag>whistleblower</video:tag>
      <video:tag>Zbigniew Błocki</video:tag>
      <video:category>News &amp; Politics</video:category>
    </video:video>
"""


def build_sitemap():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
        '        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">',
    ]
    cluster = []
    for lang in LANGS:
        cluster.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'
                       % (lang, LANG_URL[lang]))
    cluster.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>'
                   % LANG_URL["pl"])

    for lang in LANGS:
        lines.append("  <url>")
        lines.append("    <loc>%s</loc>" % LANG_URL[lang])
        lines.append("    <lastmod>%s</lastmod>" % BUILD_DATE)
        lines.append("    <changefreq>%s</changefreq>"
                     % ("weekly" if lang == "pl" else "monthly"))
        lines.append("    <priority>%s</priority>" % ("1.0" if lang == "pl" else "0.8"))
        lines.extend(cluster)
        if lang == "pl":
            lines.append(VIDEO_BLOCK.rstrip("\n"))
        lines.append("  </url>")

    for section in SECTIONS:
        lines.append("  <url>")
        lines.append("    <loc>%s/%s/</loc>" % (SITE, section["slug"]))
        lines.append("    <lastmod>%s</lastmod>" % BUILD_DATE)
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.7</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    out = os.path.join(ROOT, "sitemap.xml")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return out


PAGE_404 = """<!DOCTYPE html>
<html lang="pl" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Strona nie znaleziona (404) — KorupcjaNCN | Dr Witold Kilarski</title>
<style>
:root{--accent:#c62828;--text:#14142b;--muted:#5c5c72;--bg:#fafaf8;--border:rgba(20,20,43,0.14);}
*{box-sizing:border-box;}
body{margin:0;padding:48px 20px;background:var(--bg);color:var(--text);
     font-family:'Inter',system-ui,-apple-system,sans-serif;line-height:1.65;}
main{max-width:720px;margin:0 auto;}
h1{font-family:Georgia,'Times New Roman',serif;font-size:clamp(1.75rem,1.4rem + 1.75vw,2.5rem);margin:0 0 8px;}
h2{font-size:1.1rem;margin:32px 0 12px;}
p{margin:0 0 16px;}
.lead{font-size:1.05rem;}
.muted{color:var(--muted);font-size:0.9rem;}
ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:10px;}
li{margin:0;}
a{color:var(--accent);}
ul a{display:inline-block;padding:8px 14px;border:1px solid var(--border);border-radius:6px;
     text-decoration:none;font-size:0.9rem;color:var(--text);background:#fff;}
ul a:hover{border-color:var(--accent);color:var(--accent);}
.home{font-weight:700;}
hr{border:none;border-top:1px solid var(--border);margin:32px 0;}
</style>
</head>
<body>
<main>
<h1>404 — nie ma takiej strony</h1>
<p class="lead">Ten adres nie istnieje lub został zmieniony. Poniżej znajdziesz
najważniejsze strony serwisu dokumentującego domniemaną korupcję w Narodowym
Centrum Nauki.</p>
<p class="muted">This page does not exist or has been moved. Below are the main pages of
this whistleblower archive documenting alleged corruption at Poland's National
Science Centre (NCN).</p>
<p class="home"><a href="__BASE__/">→ Strona główna / Home</a></p>
<hr>
<h2>Strony tematyczne / Topic pages</h2>
<ul>
__ITEMS__
</ul>
<hr>
<h2>Wersje językowe / Languages</h2>
<ul>
__LANGS__
</ul>
</main>
</body>
</html>
"""


def build_404():
    items = "\n".join('<li><a href="%s/%s/">%s</a></li>' % (BASE, s["slug"], s["short"])
                      for s in SECTIONS)
    langs = "\n".join('<li><a href="%s" hreflang="%s">%s</a></li>'
                      % (LANG_PATH[l], l, LANG_BTN[l][1]) for l in LANGS)
    out = os.path.join(ROOT, "404.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(PAGE_404
                 .replace("__BASE__", BASE)
                 .replace("__ITEMS__", items)
                 .replace("__LANGS__", langs))
    return out


def check_robots():
    path = os.path.join(ROOT, "robots.txt")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    expect("Sitemap: %s/sitemap.xml" % SITE in text, "robots.txt bez wpisu Sitemap")
    expect(not re.search(r"^\s*Disallow:\s*/\S", text, re.M),
           "robots.txt blokuje sciezki (sprawdz /docs/)")
    return path


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    raw = load_source()
    id_to_url = collect_section_id_map(raw)

    written = []
    headlines = {}
    written.append(build_language_page(raw, "pl", id_to_url, headlines))
    for lang in LANGS:
        if lang == "pl":
            continue
        written.append(build_language_page(raw, lang, id_to_url))
    for section in SECTIONS:
        written.append(build_section_page(raw, section, id_to_url,
                                         headlines[section["id"]]))
    written.append(build_sitemap())
    written.append(build_404())
    check_robots()

    print("Zbudowano (%s):" % BUILD_DATE)
    for path in written:
        rel = os.path.relpath(path, ROOT)
        print("  %-42s %8.1f KB" % (rel, os.path.getsize(path) / 1024))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print("BLAD BUDOWANIA: %s" % exc, file=sys.stderr)
        sys.exit(1)
