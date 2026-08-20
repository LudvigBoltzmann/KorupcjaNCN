#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator stron statycznych KorupcjaNCN (Pakiet B + odtluszczenie 2026-08).

Zrodlo prawdy: src/index.src.html (5 jezykow w jednym pliku, bloki .lang-block).
Skrypt generuje:
  * index.html                      — PL, strona glowna po odtluszczeniu
                                      (naglowek, streszczenie, cytat, 6 kafli,
                                      skrocona chronologia, nota o autorze)
  * en/ fr/ de/ uk/ index.html      — pelna tresc w danym jezyku
  * 4 strony-huby dzialow           — nagrania, postepowania, instytucje, o-mnie
  * 17 podstron PL z trescia        — CONTENT_PAGES (dawne sekcje strony glownej)
  * nagrania/1 ... nagrania/7       — po jednej podstronie na nagranie
  * skorowidz/ (5 jezykow)          — pelna lista odnosnikow z dawnej sub-nav
  * sitemap.xml, 404.html

Uruchomienie: python3 tools/build.py
Wymagania: Python 3 + beautifulsoup4 (parser html.parser — bez lxml).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Comment

# --------------------------------------------------------------------------
# Konfiguracja
# --------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "index.src.html")

BASE = ""
SITE = "https://whistleblower.witekkilarski.org"
BUILD_DATE = "2026-08-20"
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
        "slug": "sprostowania",
        "id": "sprostowania",
        "short": "Sprostowania i korekty",
        "title": "Sprostowania i korekty | Dr Witold Kilarski",
        "desc": "Rejestr sprostowan i korekt wprowadzonych w archiwum dowodowym dotyczacym "
                "Narodowego Centrum Nauki - z data i uzasadnieniem kazdej zmiany.",
    },
    {
        "slug": "wniosek-o-kontrole-ncn",
        "id": "wniosek-kontrola-ncn",
        "short": "Wniosek o kontrolę NCN i UJ",
        "title": "Wniosek o kontrolę NCN i UJ w trybie nadzoru ministra "
                 "(art. 426 i 427) | Dr Witold Kilarski",
        "desc": "Wniosek do Ministra Nauki i Szkolnictwa Wyższego o czynności nadzorcze "
                "wobec Narodowego Centrum Nauki i Uniwersytetu Jagiellońskiego: 170 grantów "
                "przyznanych z odwołania o wartości 157 153 339 zł, 27 miesięcy bez "
                "aktualizacji listy publicznej, bezczynność Prorektora UJ ds. nauki.",
    },
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

# ==========================================================================
# ODTLUSZCZENIE STRONY GLOWNEJ — 2026-08-20
#
# Strona glowna PL zawiera wylacznie: naglowek, streszczenie sprawy, jeden
# cytat, szesc kafli dzialow, skrocona chronologie, note o autorze i stopke
# (sekcja #home-hub w src/index.src.html). Cala pozostala tresc jest
# PRZENOSZONA na podstrony — nic nie jest usuwane z witryny.
# ==========================================================================

# Sekcje przeniesione ze strony glownej na wlasne podstrony (poza SECTIONS,
# ktore mialy podstrony juz wczesniej).
MOVED_PAGES = [
    {
        "slug": "wprowadzenie",
        "id": "case",
        "short": "Wprowadzenie do sprawy",
        "title": "Wprowadzenie do sprawy — korupcja w Narodowym Centrum Nauki "
                 "| Dr Witold Kilarski",
        "desc": "Wprowadzenie do sprawy: ultimatum dyrektora NCN z 29 maja 2020 r., "
                "e-mail z konta NCN z 1 czerwca 2020 r., związek z wnioskiem NAWA "
                "Polskie Powroty i rodzaje zebranych dowodów.",
    },
    {
        "slug": "chronologia",
        "id": "timeline",
        "short": "Pełna chronologia",
        "title": "Pełna chronologia sprawy NCN (2009–2026) | Dr Witold Kilarski",
        "desc": "Pełna chronologia sprawy: kariera naukowa, ultimatum z 29 maja 2020 r., "
                "konkursy NAWA Polskie Powroty, odmowy prokuratury i postępowania "
                "sądowe przeciwko sygnaliście.",
    },
    {
        "slug": "cv",
        "id": "about",
        "short": "O mnie i CV",
        "title": "Dr Witold Kilarski — nota biograficzna i CV | archiwum sygnalisty",
        "desc": "Nota biograficzna i pełne CV dr. Witolda Kilarskiego: Uppsala, EPFL "
                "Lozanna, Bordeaux, University of Chicago, badania nad układem "
                "limfatycznym i wniosek NAWA Polskie Powroty.",
    },
    {
        "slug": "wum-blocki-cyngiel",
        "id": "blocki-cyngiel",
        "short": "WUM odcina mnie po piśmie dyrektora NCN",
        "title": "WUM odcina mnie po piśmie Dyrektora NCN — e-mail z 11 marca 2022 r. "
                 "| Dr Witold Kilarski",
        "desc": "E-mail Warszawskiego Uniwersytetu Medycznego z 11 marca 2022 r.: po "
                "piśmie dyrektora NCN uczelnia odmawia podpisania wniosku o ponowne "
                "rozpatrzenie sprawy do NAWA (Polskie Powroty 2021).",
    },
    {
        "slug": "list-otwarty",
        "id": "list-otwarty",
        "short": "List otwarty do Premiera i Ministra",
        "title": "List otwarty do Prezesa Rady Ministrów i Ministra Sprawiedliwości "
                 "| Dr Witold Kilarski",
        "desc": "List otwarty z 13 lipca 2026 r. w sprawie systemowej odmowy ścigania "
                "korupcji, szantażu i nepotyzmu w Narodowym Centrum Nauki oraz NAWA.",
    },
    {
        "slug": "pomoc-ukraincom",
        "id": "ukraina",
        "short": "Pomoc Ukraińcom",
        "title": "Pomoc Ukraińcom zastraszanym w Polsce | Dr Witold Kilarski",
        "desc": "Otwarta oferta pomocy dla Ukraińców nękanych lub zastraszanych w Polsce "
                "— kontakt całodobowy i plakat informacyjny po polsku i ukraińsku.",
    },
    {
        "slug": "kulturowe-analogie",
        "id": "kulturowe-analogie",
        "short": "Kulturowe analogie",
        "title": "Kulturowe analogie — pieśni, wiersze i sceny wokół tej sprawy "
                 "| Dr Witold Kilarski",
        "desc": "Kulturowe komentarze do sprawy sygnalisty NCN: Herbert, Tuwim, "
                "Mickiewicz, Kaczmarski i inne utwory, które rezonują z tą historią.",
    },
    {
        "slug": "dyskusja",
        "id": "comments",
        "short": "Dyskusja",
        "title": "Dyskusja — komentarze czytelników | Dr Witold Kilarski",
        "desc": "Miejsce na komentarze i pytania czytelników archiwum dowodowego "
                "dotyczącego domniemanej korupcji w Narodowym Centrum Nauki.",
    },
]

# Siedem nagran audio — kazde na wlasnej podstronie /nagrania/N/.
# "analiza" = numer tego samego nagrania w dokumencie
# analiza_nagran_audio_kompletna (numeracja 1-10). Zadnej numeracji nie
# zmieniamy — tabela przeliczenia jest w /sprostowania/.
RECORDINGS = [
    {
        "n": 1, "id": "interview", "slug": "nagrania/1",
        "short": "Nagranie 1 — 29 maja 2020",
        "date": "29 maja 2020 r.",
        "people": "osoba NN i dr Witold Kilarski",
        "length": "ok. 1 godz. 2 min",
        "analiza": "1",
        "title": "Nagranie 1 (29 maja 2020) — rozmowa z osobą NN po ultimatum "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 1 z 29 maja 2020 r.: rozmowa z osobą NN po ultimatum "
                "dyrektora NCN — szantaż, dostęp do prywatnej korespondencji, "
                "recenzje Mudelsee. Transkrypcja tematyczna i odtwarzacz.",
    },
    {
        "n": 2, "id": "interview-3-4", "slug": "nagrania/2",
        "short": "Nagranie 2 — 2 czerwca 2020",
        "date": "2 czerwca 2020 r.",
        "people": "osoba NN i dyrektor NCN Zbigniew Błocki",
        "length": "ok. 1 godz. 36 min",
        "analiza": "2",
        "title": "Nagranie 2 (2 czerwca 2020) — spotkanie osoby NN z dyrektorem NCN "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 2 z 2 czerwca 2020 r.: nagrane spotkanie osoby NN "
                "z dyrektorem NCN Zbigniewem Błockim — powrót do ultimatum "
                "w sprawie wniosku NAWA i listy rankingowe.",
    },
    {
        "n": 3, "id": "interview-4", "slug": "nagrania/3",
        "short": "Nagranie 3 — 4 czerwca 2020",
        "date": "4 czerwca 2020 r.",
        "people": "osoba NN i dyrektor NCN Zbigniew Błocki",
        "length": "ok. 1 godz. 52 min",
        "analiza": "3",
        "title": "Nagranie 3 (4 czerwca 2020) — trzecia rozmowa ze Zbigniewem Błockim "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 3 z 4 czerwca 2020 r.: trzecia rozmowa ze Zbigniewem Błockim "
                "— przeniesienie odpowiedzialności na osobę NN i relacje "
                "o nastrojach wśród pracowników NCN.",
    },
    {
        "n": 4, "id": "rec-4", "slug": "nagrania/4",
        "short": "Nagranie 4 — 10 października 2020",
        "date": "10 października 2020 r.",
        "people": "osoba NN i dr Witold Kilarski",
        "length": "ok. 45 min",
        "analiza": "5",
        "title": "Nagranie 4 (10 października 2020) — osoba NN o chęci odejścia z NCN "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 4 z 10 października 2020 r.: osoba NN o systemie przyznawania "
                "grantów, nieprawidłowościach w NCN i zamiarze odejścia z instytucji.",
    },
    {
        "n": 5, "id": "rec-5a", "slug": "nagrania/5",
        "short": "Nagranie 5 — 20 marca 2021 (części A i B)",
        "date": "20 marca 2021 r.",
        "people": "osoba NN i dr Witold Kilarski",
        "length": "ok. 2 godz. 21 min (dwie części)",
        "analiza": "7 i 8",
        "title": "Nagranie 5 (20 marca 2021) — jedna rozmowa w dwóch częściach "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 5 z 20 marca 2021 r. w dwóch częściach: sprawa Mudelsee "
                "i „14 identycznych recenzji\", konflikty interesów w Radzie NCN "
                "oraz reakcje wewnątrz instytucji.",
    },
    {
        "n": 6, "id": "rec-6", "slug": "nagrania/6",
        "short": "Nagranie 6 — telefon osoby NN do mnie",
        "date": "nieustalona (plik audio niepublikowany)",
        "people": "osoba NN dzwoni z Krakowa na komórkę dr. Witolda Kilarskiego "
                  "przebywającego w Jareniówce",
        "length": "nieustalony — plik audio niepublikowany",
        "analiza": "9",
        "title": "Nagranie 6 — telefon osoby NN do dr. Kilarskiego "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 6: osoba NN dzwoni do dr. Kilarskiego — eskalacja konfliktu "
                "z prof. Marcinem Drągiem, stanowisko prof. Melody Swartz i decyzja "
                "o drodze sądowej. Plik audio nie jest publikowany.",
    },
    {
        "n": 7, "id": "rec-7", "slug": "nagrania/7",
        "short": "Nagranie 7 — 30 września 2021",
        "date": "30 września 2021 r.",
        "people": "osoba NN i dr Witold Kilarski",
        "length": "ok. 40 min",
        "analiza": "10",
        "title": "Nagranie 7 (30 września 2021) — mechanizm zniszczenia "
                 "| Dr Witold Kilarski",
        "desc": "Nagranie 7 z 30 września 2021 r.: skąd dyrektor NCN wiedział "
                "o wniosku NAWA, manipulacja progiem punktowym w panelu NAWA "
                "i powód usunięcia osoby NN z NCN.",
    },
]

RECORDINGS_BY_ID = {r["id"]: r for r in RECORDINGS}

NUMBERING_NOTE_URL = BASE + "/sprostowania/#errata-numeracja-nagran"
NUMBERING_NOTE_TEXT = (
    "Numeracja: to nagranie %s na stronie odpowiada nagraniu %s w dokumencie "
    "analiza_nagran_audio_kompletna — zob. notę o numeracji z 20 sierpnia 2026 r."
)

# Strony-huby szesciu dzialow menu. Zawieraja wylacznie nawigacje (pionowa
# lista podstron dzialu) — zadnej tresci dowodowej.
HUBS = [
    {
        "slug": "nagrania",
        "short": "Nagrania",
        "h1": "Nagrania audio (2020–2021)",
        "title": "Nagrania audio 1–7 — archiwum dowodów sygnalisty NCN "
                 "| Dr Witold Kilarski",
        "desc": "Siedem nagrań audio z lat 2020–2021 dokumentujących domniemany "
                "szantaż i nieprawidłowości w Narodowym Centrum Nauki. Każde "
                "nagranie na osobnej podstronie, z opisem tematycznym i odtwarzaczem.",
        "intro": "Każde nagranie ma osobną podstronę: opis, uczestnicy, czas trwania, "
                 "odtwarzacz, podział tematyczny (sekcje A–G) i notę źródłową. "
                 "Nagrania nie odtwarzają się automatycznie.",
        "items": [],  # uzupelniane z RECORDINGS
    },
    {
        "slug": "postepowania",
        "short": "Postępowania",
        "h1": "Postępowania — prokuratura, sądy, egzekucja, nadzór ministra",
        "title": "Postępowania: prokuratura, sądy, komornik, wniosek o kontrolę "
                 "| Dr Witold Kilarski",
        "desc": "Wszystkie postępowania w sprawie: odmowy wszczęcia śledztwa, sprawy "
                "sądowe przeciwko sygnaliście, egzekucja komornicza Km 834/26 "
                "i wniosek o kontrolę NCN oraz UJ w trybie nadzoru ministra.",
        "intro": "Postępowania prowadzone w tej sprawie — zarówno te, których "
                 "organy odmówiły, jak i te wszczęte przeciwko sygnaliście.",
        "items": ["prokuratura", "sprawy-sadowe", "wyrok-kafkowski",
                  "sprawa-komornika", "wniosek-o-kontrole-ncn"],
    },
    {
        "slug": "instytucje",
        "short": "Instytucje",
        "h1": "Instytucje — NCN, Uniwersytet Jagielloński, WUM",
        "title": "Instytucje: NCN, Uniwersytet Jagielloński, WUM "
                 "| Dr Witold Kilarski",
        "desc": "Dokumentacja dotycząca instytucji: maszynowe recenzje NCN (sprawa "
                "Mudelsee), bezczynność Uniwersytetu Jagiellońskiego, pismo "
                "dyrektora NCN do WUM oraz wątek Błocki–Babik–Liana.",
        "intro": "Cztery wątki instytucjonalne: co zrobiły — i czego nie zrobiły — "
                 "instytucje, do których kierowano zgłoszenia.",
        "items": ["maszynowe-recenzje-ncn", "bezczynnosc-uj",
                  "wum-blocki-cyngiel", "blocki-babik-liana"],
    },
    {
        "slug": "o-mnie",
        "short": "O mnie",
        "h1": "O mnie — biografia, sprostowania, kontakt",
        "title": "O mnie — CV, sprostowania i kontakt | Dr Witold Kilarski",
        "desc": "Nota biograficzna i CV dr. Witolda Kilarskiego, rejestr sprostowań "
                "i korekt, dane kontaktowe oraz pozostałe materiały: list otwarty, "
                "pomoc Ukraińcom, kulturowe analogie i dyskusja.",
        "intro": "Kim jestem, jak poprawiam własne błędy i jak się ze mną skontaktować. "
                 "Kontakt: witek.kilarski@gmail.com, +48 782 473 130.",
        "items": ["cv", "sprostowania", "list-otwarty", "pomoc-ukraincom",
                  "kulturowe-analogie", "dyskusja"],
    },
]

HUB_BY_SLUG = {h["slug"]: h for h in HUBS}

# Skorowidz: pelna lista odnosnikow z dawnego drugiego rzedu zakladek
# (nav.sub-nav). Rzad zakladek zniknal z witryny, ale ani jeden odnosnik nie
# zostal usuniety — wszystkie sa tutaj.
SKOROWIDZ_META = {
    "pl": ("Skorowidz dokumentów i sekcji | Dr Witold Kilarski",
           "Pełny skorowidz archiwum: wszystkie dokumenty, pisma i sekcje "
           "dotyczące domniemanej korupcji w Narodowym Centrum Nauki.",
           "Skorowidz dokumentów i sekcji",
           "Pełna lista odnośników z dawnego rzędu zakładek. Nic nie zostało "
           "usunięte — zmieniło się tylko miejsce."),
    "en": ("Index of documents and sections | Dr Witold Kilarski",
           "Full index of the archive: every document, letter and section "
           "documenting alleged corruption at Poland's National Science Centre.",
           "Index of documents and sections",
           "The complete list of links from the former tab row. Nothing was "
           "removed — only moved."),
    "fr": ("Index des documents et sections | Dr Witold Kilarski",
           "Index complet des archives : tous les documents, courriers et sections "
           "concernant la corruption présumée au Centre national des sciences.",
           "Index des documents et sections",
           "La liste complète des liens de l'ancienne rangée d'onglets. Rien n'a "
           "été supprimé — seulement déplacé."),
    "de": ("Index der Dokumente und Abschnitte | Dr Witold Kilarski",
           "Vollständiger Index des Archivs: alle Dokumente, Schreiben und "
           "Abschnitte zur mutmaßlichen Korruption am NCN.",
           "Index der Dokumente und Abschnitte",
           "Die vollständige Liste der Links aus der früheren Registerkartenreihe. "
           "Nichts wurde entfernt — nur verschoben."),
    "uk": ("Покажчик документів і розділів | Dr Witold Kilarski",
           "Повний покажчик архіву: усі документи, листи та розділи щодо ймовірної "
           "корупції в Національному науковому центрі Польщі.",
           "Покажчик документів і розділів",
           "Повний список посилань із колишнього рядка вкладок. Нічого не "
           "видалено — лише переміщено."),
}

# Dokladnie szesc zakladek menu (Zadanie 3). Etykiety PL dokladnie jak
# w zleceniu. Dla jezykow bez tlumaczenia etykiet uzywamy wersji angielskiej
# (odnotowane w raporcie).
NAV_TABS = [
    ("sprawa", BASE + "/", {"pl": "Sprawa", "en": "Case", "fr": "Case",
                            "de": "Case", "uk": "Case"}),
    ("nagrania", BASE + "/nagrania/", {"pl": "Nagrania", "en": "Recordings",
                                       "fr": "Recordings", "de": "Recordings",
                                       "uk": "Recordings"}),
    ("dokumenty", BASE + "/dokumenty/", {"pl": "Dokumenty", "en": "Documents",
                                         "fr": "Documents", "de": "Documents",
                                         "uk": "Documents"}),
    ("postepowania", BASE + "/postepowania/", {"pl": "Postępowania",
                                               "en": "Proceedings",
                                               "fr": "Proceedings",
                                               "de": "Proceedings",
                                               "uk": "Proceedings"}),
    ("instytucje", BASE + "/instytucje/", {"pl": "Instytucje", "en": "Institutions",
                                           "fr": "Institutions",
                                           "de": "Institutions",
                                           "uk": "Institutions"}),
    ("o-mnie", BASE + "/o-mnie/", {"pl": "O mnie", "en": "About me",
                                   "fr": "About me", "de": "About me",
                                   "uk": "About me"}),
]

FOOTER_LINKS = {
    "pl": [(BASE + "/skorowidz/", "Pełne archiwum — skorowidz"),
           (BASE + "/nagrania/", "Nagrania 1–7"),
           (BASE + "/sprostowania/", "Sprostowania i korekty")],
    "en": [(BASE + "/en/skorowidz/", "Full archive — index"),
           (BASE + "/nagrania/", "Recordings 1–7"),
           (BASE + "/sprostowania/", "Corrections")],
    "fr": [(BASE + "/fr/skorowidz/", "Full archive — index"),
           (BASE + "/nagrania/", "Recordings 1–7"),
           (BASE + "/sprostowania/", "Corrections")],
    "de": [(BASE + "/de/skorowidz/", "Full archive — index"),
           (BASE + "/nagrania/", "Recordings 1–7"),
           (BASE + "/sprostowania/", "Corrections")],
    "uk": [(BASE + "/uk/skorowidz/", "Full archive — index"),
           (BASE + "/nagrania/", "Recordings 1–7"),
           (BASE + "/sprostowania/", "Corrections")],
}

# Wszystkie strony PL z trescia (dawne SECTIONS + sekcje przeniesione).
CONTENT_PAGES = SECTIONS + MOVED_PAGES
PAGE_BY_ID = {p["id"]: p for p in CONTENT_PAGES}
PAGE_BY_SLUG = {p["slug"]: p for p in CONTENT_PAGES}

# Przypisanie podstron do dzialow (do bloku "Powiazane strony").
GROUP_OF_SLUG = {}
for _hub in HUBS:
    for _slug in _hub["items"]:
        GROUP_OF_SLUG[_slug] = _hub["slug"]
GROUP_OF_SLUG["dokumenty"] = "dokumenty"
GROUP_OF_SLUG["chronologia"] = "sprawa"
GROUP_OF_SLUG["wprowadzenie"] = "sprawa"
for _rec in RECORDINGS:
    GROUP_OF_SLUG[_rec["slug"]] = "nagrania"

# Sekcje strony glownej, ktore zostaja na home (poza <main> hero i stopka).
HOME_KEEP_SECTION_IDS = {"home-hub"}

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

# Punkt 8 + decyzja autora z 20 sierpnia 2026 r.: pliku nie publikujemy i nie
# obiecujemy terminu; opis nagrania i numeracja zostaja bez zmian.
MISSING_AUDIO_NOTE = {
    "pl": ("Plik audio tego nagrania nie jest publikowany — nie mam pewności, "
           "czy nie jest duplikatem innej z opublikowanych rozmów. Opis tematyczny "
           "i numeracja pozostają bez zmian. ",
           "Zob. notę w Sprostowaniach (20 sierpnia 2026 r.)"),
    "en": ("The audio file for this recording is not published — it may be a duplicate "
           "of one of the conversations already online. The topical description and "
           "the numbering stay unchanged. ",
           "See the note in Corrections (20 August 2026)"),
    "fr": ("Le fichier audio de cet enregistrement n'est pas publié — il peut s'agir "
           "d'un doublon d'une conversation déjà en ligne. La description thématique "
           "et la numérotation restent inchangées. ",
           "Voir la note dans les Rectifications (20 août 2026)"),
    "de": ("Die Audiodatei dieser Aufnahme wird nicht veröffentlicht — sie kann ein "
           "Duplikat eines bereits veröffentlichten Gesprächs sein. Beschreibung und "
           "Numerierung bleiben unverändert. ",
           "Siehe die Notiz in den Korrekturen (20. August 2026)"),
    "uk": ("Аудіофайл цього запису не публікується — можливо, це дублікат іншої "
           "вже опублікованої розмови. Опис і нумерація залишаються без змін. ",
           "Див. нотатку в Розділі виправлень (20 серпня 2026 р.)"),
}
MISSING_AUDIO_NOTE_URL = BASE + "/sprostowania/#errata-nagranie-6-plik"

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

/* ============================================================
   Odtluszczenie strony glownej (2026-08-20):
   menu sześciu zakładek, kafle działów, huby, skorowidz,
   szerokosc kolumny tekstu i odstepy miedzy sekcjami.
   ============================================================ */

/* --- MENU: jeden rzad, szesc klikalnych zakladek, bez hovera --- */
.nav-links{display:flex;gap:var(--space-2);flex-wrap:nowrap;align-items:center;}
@media (min-width:768px){.nav-links{display:flex !important;}}
.nav-links .nav-link{padding:var(--space-2) var(--space-3);border-radius:6px;white-space:nowrap;}
.nav-links .nav-link[aria-current="page"]{color:#fff;background:rgba(255,255,255,0.14);font-weight:700;}
.nav-links .nav-link:focus-visible,.lang-btn:focus-visible,.mobile-menu-btn:focus-visible{outline:2px solid #ffd166;outline-offset:2px;}
@media (max-width:900px){
  .nav-links{position:absolute;left:0;right:0;top:100%;display:none !important;
    flex-direction:column;align-items:stretch;gap:0;
    background:var(--color-header-bg);border-bottom:1px solid rgba(255,255,255,0.12);
    padding:var(--space-2) var(--space-4) var(--space-4);}
  .nav-links.open{display:flex !important;}
  .nav-links .nav-link{padding:var(--space-3) 0;border-bottom:1px solid rgba(255,255,255,0.08);}
  .mobile-menu-btn{display:flex !important;}
  .header-inner{position:relative;}
}
@media (min-width:901px){.mobile-menu-btn{display:none !important;}}

/* --- STRONA GLOWNA: kolumna tekstu, cytat, kafle, chronologia --- */
#home-hub{max-width:900px;margin:0 auto;padding-left:var(--space-5);padding-right:var(--space-5);
  text-align:left;}
#home-hub h2{margin-top:var(--space-12);}
#home-hub > .lang-block > h2:first-of-type{margin-top:0;}
#home-hub p{max-width:70ch;}
.hero-name{font-family:var(--font-sans);font-size:var(--text-sm);font-weight:600;
  letter-spacing:0.02em;color:var(--color-hero-muted);margin:0 0 var(--space-2);}
.home-quote{margin:var(--space-8) 0;padding:var(--space-6);border-left:4px solid var(--color-accent);
  background:#fef9f0;border-radius:4px;}
.home-quote p{font-size:var(--text-lg);font-style:italic;margin:0 0 var(--space-3);}
.home-quote footer{font-style:normal;font-size:var(--text-sm);color:var(--color-text-muted);}
.hub-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
  gap:var(--space-5);margin:var(--space-6) 0 var(--space-4);text-align:left;}
.hub-card{border:1px solid var(--color-border);border-radius:8px;padding:var(--space-5);
  background:var(--color-surface,#fff);}
.hub-card h3{margin:0 0 var(--space-3);font-size:var(--text-lg);}
.hub-card p{margin:0 0 var(--space-3);font-size:var(--text-sm);line-height:1.6;}
.hub-card-cta{margin:0;}
.hub-card-cta a{display:inline-block;font-weight:700;color:var(--color-accent);
  border:1px solid var(--color-accent);border-radius:6px;padding:var(--space-2) var(--space-4);
  font-size:var(--text-sm);}
.hub-card-cta a:hover{background:var(--color-accent);color:#fff;}
.home-chrono{list-style:none;padding:0;margin:0 0 var(--space-4);text-align:left;max-width:70ch;}
.home-chrono li{padding:var(--space-3) 0;border-bottom:1px solid var(--color-border);
  font-size:var(--text-sm);line-height:1.6;}
.home-about{max-width:70ch;}

/* --- STRONY-HUBY I SKOROWIDZ --- */
.hub-page{max-width:820px;margin:0 auto;padding:var(--space-8) var(--space-5);text-align:left;}
.hub-page h1{font-family:var(--font-serif);font-size:var(--text-2xl);line-height:1.2;
  margin:0 0 var(--space-4);}
.hub-page .hub-intro{font-size:var(--text-base);color:var(--color-text-muted);
  margin:0 0 var(--space-8);max-width:70ch;}
.hub-list{list-style:none;padding:0;margin:0;}
.hub-list > li{border-top:1px solid var(--color-border);padding:var(--space-5) 0;}
.hub-list > li:last-child{border-bottom:1px solid var(--color-border);}
.hub-list a.hub-list-title{font-family:var(--font-serif);font-size:var(--text-lg);font-weight:700;}
.hub-list p{margin:var(--space-2) 0 0;font-size:var(--text-sm);color:var(--color-text-muted);
  max-width:70ch;}
.skorowidz h2{font-family:var(--font-serif);font-size:var(--text-xl);
  margin:var(--space-8) 0 var(--space-3);}
.skorowidz h3{font-size:var(--text-sm);text-transform:uppercase;letter-spacing:0.08em;
  color:var(--color-accent);margin:var(--space-5) 0 var(--space-2);}
.skorowidz ul{list-style:none;padding:0;margin:0;}
.skorowidz li{padding:4px 0;font-size:var(--text-sm);}

/* --- PODSTRONY NAGRAN: numeracja, nawigacja poprzednie/nastepne --- */
.rec-meta{list-style:none;padding:var(--space-4);margin:0 0 var(--space-6);
  border:1px solid var(--color-border);border-radius:6px;font-size:var(--text-sm);
  text-align:left;max-width:70ch;}
.rec-meta li{padding:2px 0;}
.rec-numbering{font-size:var(--text-sm);color:var(--color-text-muted);
  border-left:3px solid #b45309;padding:var(--space-2) var(--space-4);
  margin:0 0 var(--space-6);text-align:left;max-width:70ch;}
.rec-prevnext{display:flex;flex-wrap:wrap;gap:var(--space-4);justify-content:space-between;
  margin:var(--space-8) 0 var(--space-4);font-size:var(--text-sm);}
.rec-prevnext a{font-weight:600;}
.errata-tabela{border-collapse:collapse;margin:var(--space-4) 0;font-size:var(--text-sm);}
.errata-tabela th,.errata-tabela td{border:1px solid var(--color-border);
  padding:6px 10px;text-align:left;}

/* --- CZYTELNOSC: naglowek H1 na podstronach, odstepy miedzy sekcjami --- */
main .section h1,main .interview-section h1,main .komornik-section h1,
main .listotwarty-section h1,main .ukraina-section h1,main .kultura-section h1,
main .comments-section h1{font-family:var(--font-serif);font-size:var(--text-2xl);
  font-weight:700;line-height:1.2;letter-spacing:-0.015em;
  margin:0 0 var(--space-6);color:var(--color-text);}
main > section{margin-bottom:var(--space-12);}
main p{max-width:78ch;}
main .section p,main .interview-section p{line-height:1.7;}

/* Akapity i listy czytamy od lewej (naglowki zostaja wysrodkowane jak dotad):
   dlugie transkrypcje wysrodkowane sa mecznie trudne do czytania. */
main .section p,main .section li,main .interview-section p,main .interview-section li,
main .komornik-section p,main .komornik-section li,main .listotwarty-section p,
main .listotwarty-section li,main .ukraina-section p,main .ukraina-section li,
main .kultura-section p,main .kultura-section li,main blockquote,
main .footnote-meta,main .przypis-sprostowanie,main .redaction-note{text-align:left;}
main .section p,main .interview-section p,main .komornik-section p{margin-left:auto;margin-right:auto;}

/* --- FILM: zaslona zamiast osadzonego odtwarzacza (szybkosc + prywatnosc) --- */
.yt-facade{position:relative;display:block;width:100%;padding:0;border:0;
  background:#000;cursor:pointer;border-radius:6px;overflow:hidden;line-height:0;}
.yt-facade img{width:100%;height:auto;display:block;opacity:0.92;transition:opacity 0.2s;}
.yt-facade:hover img,.yt-facade:focus-visible img{opacity:1;}
.yt-facade .yt-play{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:68px;height:48px;border-radius:8px;background:rgba(200,30,30,0.92);
  display:flex;align-items:center;justify-content:center;}
.yt-facade .yt-play::after{content:"";display:block;width:0;height:0;
  border-left:18px solid #fff;border-top:11px solid transparent;
  border-bottom:11px solid transparent;margin-left:4px;}
.yt-facade .yt-caption{position:absolute;left:0;right:0;bottom:0;
  font-family:var(--font-sans);font-size:var(--text-xs);line-height:1.4;color:#fff;
  background:linear-gradient(transparent,rgba(0,0,0,0.75));padding:24px 12px 10px;
  text-align:left;}
.yt-facade:focus-visible{outline:2px solid #ffd166;outline-offset:2px;}
.yt-facade-plain{padding-bottom:56.25%;height:0;
  background:linear-gradient(160deg,#1c1c2e,#2c2c44);}
.yt-facade-plain .yt-caption{background:none;padding:12px;bottom:auto;top:60%;
  font-size:var(--text-sm);}
"""

# Film dokumentalny: zaslona (facade) zamiast osadzonego odtwarzacza YouTube.
# Do kliknięcia strona nie wysyla zadnego zapytania do YouTube — miniatura jest
# lokalna. Zero skryptow firm trzecich i zero ciasteczek przed kliknieciem.
YT_EMBED_MARK = "youtube.com/embed"
YT_THUMB = "docs/yt-Z7DH_iRY78w.jpg"
YT_FACADE_LABEL = {
    "pl": ("Odtwórz film dokumentalny", "Kliknięcie uruchamia odtwarzacz YouTube"),
    "en": ("Play the documentary", "Clicking loads the YouTube player"),
    "fr": ("Lire le documentaire", "Le clic charge le lecteur YouTube"),
    "de": ("Dokumentarfilm abspielen", "Ein Klick lädt den YouTube-Player"),
    "uk": ("Відтворити документальний фільм", "Натискання завантажить плеєр YouTube"),
}

YT_FACADE_JS = """
(function(){
  document.addEventListener('click', function(e){
    var btn = e.target.closest && e.target.closest('.yt-facade');
    if (!btn) return;
    var src = btn.getAttribute('data-yt');
    if (!src) return;
    var box = document.createElement('div');
    box.style.cssText = 'position:relative;padding-bottom:56.25%;height:0;overflow:hidden';
    var f = document.createElement('iframe');
    f.src = src + (src.indexOf('?') > -1 ? '&' : '?') + 'autoplay=1';
    f.title = btn.getAttribute('aria-label') || 'video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.setAttribute('allowfullscreen','');
    f.setAttribute('frameborder','0');
    f.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%';
    box.appendChild(f);
    btn.replaceWith(box);
  });
})();
"""

# Menu mobilne: Escape zamyka, aria-expanded utrzymane (WCAG 2.1.1).
MENU_A11Y_JS = """
(function(){
  var btn = document.getElementById('mobile-menu-btn');
  var nav = document.getElementById('nav-links');
  if (!btn || !nav) return;
  function close(){ nav.classList.remove('open'); btn.setAttribute('aria-expanded','false'); }
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && nav.classList.contains('open')) { close(); btn.focus(); }
  });
  nav.addEventListener('click', function(e){ if (e.target.closest('a')) close(); });
})();
"""

HASH_REDIRECT_JS = """
(function(){
  var m = {en:'/en/', fr:'/fr/', de:'/de/', uk:'/uk/', pl:'/'};
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
        # Nazwy moga byc juz poprawione w zrodle - wtedy nie ma czego zamieniac.
        expect(old in raw or new in raw,
               "brak w zrodle sciezki audio (ani starej, ani nowej): %s" % old)
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
        text, link_label = MISSING_AUDIO_NOTE[lang]
        note.append(text)
        link = soup.new_tag("a", href=MISSING_AUDIO_NOTE_URL)
        link.string = link_label
        note.append(link)
        audio.replace_with(note)
        note.insert_before(Comment(" plik audio nagrania 6 nieopublikowany "
                                   "(decyzja autora, 20 sierpnia 2026) "))



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
        # UWAGA (2026-08-20): poprzednia wersja wzorca konczyla dopasowanie na
        # pierwszym "});" wewnatrz petli forEach, wiec wstawiony nawias
        # klamrowy trafial w srodek wywolania i psul CALY skrypt (7,2 KB JS
        # nie wykonywal sie w ogole). Wzorzec obejmuje teraz oba domkniecia.
        match = re.search(
            r"([ \t]*mobileMenuBtn\.addEventListener\('click'.*?\n[ \t]*\}\);\n"
            r"[ \t]*// Close mobile menu when nav link is clicked\n"
            r"[ \t]*navLinks\.querySelectorAll.*?\n[ \t]*\}\);\n[ \t]*\}\);\n)",
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


def page_short(slug):
    """Krotka nazwa strony o danym slugu (podstrona tresci, nagranie albo hub)."""
    if slug in PAGE_BY_SLUG:
        return PAGE_BY_SLUG[slug]["short"]
    for rec in RECORDINGS:
        if rec["slug"] == slug:
            return rec["short"]
    if slug in HUB_BY_SLUG:
        return HUB_BY_SLUG[slug]["short"]
    raise BuildError("nieznany slug: %s" % slug)


def siblings_of(slug):
    """Pozostale strony tego samego dzialu — do bloku „Powiazane strony”."""
    group = GROUP_OF_SLUG.get(slug)
    out = []
    if group == "nagrania":
        out = [r["slug"] for r in RECORDINGS if r["slug"] != slug]
    elif group == "sprawa":
        out = [s for s in ("wprowadzenie", "chronologia") if s != slug]
    elif group in HUB_BY_SLUG:
        out = [s for s in HUB_BY_SLUG[group]["items"] if s != slug]
    return out


def build_related(soup, current_slug):
    nav = soup.new_tag("nav")
    nav["class"] = ["related-pages"]
    nav["aria-label"] = "Powiązane strony"
    heading = soup.new_tag("h2")
    heading.string = "Powiązane strony"
    nav.append(heading)
    ul = soup.new_tag("ul")

    targets = []
    group = GROUP_OF_SLUG.get(current_slug)
    if group in HUB_BY_SLUG:
        targets.append((BASE + "/" + group + "/", HUB_BY_SLUG[group]["short"]))
    for slug in siblings_of(current_slug):
        targets.append((BASE + "/" + slug + "/", page_short(slug)))
    targets.append((BASE + "/skorowidz/", "Skorowidz archiwum"))
    targets.append((BASE + "/", "Strona główna"))

    for href, label in targets:
        li = soup.new_tag("li")
        a = soup.new_tag("a", href=href)
        a.string = label
        li.append(a)
        ul.append(li)
    nav.append(ul)
    return nav


# --------------------------------------------------------------------------
# Menu szesciu zakladek, stopka, elementy wspolne (2026-08-20)
# --------------------------------------------------------------------------

def install_nav(soup, lang, current=None):
    """Dokladnie szesc klikalnych zakladek w jednym rzedzie; drugi rzad znika."""
    nav = soup.find("nav", id="nav-links")
    expect(nav is not None, "brak nav#nav-links")
    nav.clear()
    for key, href, labels in NAV_TABS:
        a = soup.new_tag("a", href=href)
        a["class"] = ["nav-link"]
        a["data-nav"] = key
        if key == current:
            a["aria-current"] = "page"
        span = soup.new_tag("span")
        span["class"] = ["nav-" + lang]
        span.string = labels[lang]
        a.append(span)
        nav.append(a)

    sub = soup.find("nav", class_="sub-nav")
    if sub is not None:
        sub.decompose()

    script = soup.new_tag("script")
    script.string = MENU_A11Y_JS
    soup.body.append(script)


def install_footer_links(soup, lang):
    footer = soup.find("footer", class_="site-footer")
    expect(footer is not None, "brak stopki")
    block = footer.find("div", class_="lang-block")
    expect(block is not None, "stopka bez bloku jezykowego")
    nav = soup.new_tag("nav")
    nav["class"] = ["footer-links"]
    nav["aria-label"] = "Stopka"
    for i, (href, label) in enumerate(FOOTER_LINKS[lang]):
        if i:
            nav.append(" · ")
        a = soup.new_tag("a", href=href)
        a.string = label
        nav.append(a)
    block.append(nav)


def strip_inpage_navs(soup):
    """Usuwa wewnatrzstronowe rzedy zakladek (.section-nav, .section-jumpnav)."""
    removed = 0
    for nav in soup.select("nav.section-nav, nav.section-jumpnav"):
        nav.decompose()
        removed += 1
    return removed


def promote_first_heading(container):
    """Pierwszy <h2> podstrony staje sie <h1> (hierarchia H1/H2/H3)."""
    heading = container.find("h2")
    if heading is not None:
        heading.name = "h1"
        return heading.get_text(" ", strip=True)
    return None


def build_breadcrumb_for(soup, label, hub_slug=None):
    nav = soup.new_tag("nav")
    nav["class"] = ["breadcrumb"]
    nav["aria-label"] = "Breadcrumb"
    home = soup.new_tag("a", href=BASE + "/")
    home.string = "Strona główna"
    nav.append(home)
    if hub_slug and hub_slug in HUB_BY_SLUG:
        nav.append(" › ")
        hub = soup.new_tag("a", href=BASE + "/" + hub_slug + "/")
        hub.string = HUB_BY_SLUG[hub_slug]["short"]
        nav.append(hub)
    nav.append(" › ")
    current = soup.new_tag("span")
    current.string = label
    nav.append(current)
    return nav


# --------------------------------------------------------------------------
# Przekierowanie dawnych kotwic strony glownej na nowe adresy
# --------------------------------------------------------------------------

def anchor_redirect_js(mapping):
    """Dawne #kotwice strony glownej -> nowe adresy podstron.

    GitHub Pages nie obsluguje przekierowan 301 po stronie serwera (a fragment
    URL nigdy nie dociera do serwera), wiec zachowanie dawnych odnosnikow
    realizuje przekierowanie po stronie przegladarki — natychmiastowe,
    z location.replace (bez wpisu w historii, jak przy 301).
    """
    return (
        "\n(function(){\n  var m = "
        + json.dumps(mapping, ensure_ascii=False, sort_keys=True)
        + ";\n  var h = location.hash.replace('#','');"
        "\n  if (h && m[h]) { location.replace(m[h]); }\n})();\n"
    )


def install_anchor_redirect(soup, mapping):
    script = soup.new_tag("script")
    script.string = anchor_redirect_js(mapping)
    anchor = soup.head.find("meta", attrs={"name": "viewport"})
    if anchor is not None:
        anchor.insert_after(script)
    else:
        soup.head.insert(0, script)


def collect_old_anchors(raw, id_to_url):
    """Kotwice, ktore wystepowaly w zrodle jako <a href="#..."> i zmienily adres."""
    frags = set(re.findall(r'href="#([^"]+)"', raw))
    mapping = {}
    for frag in sorted(frags):
        if frag in NATIVE_FRAGMENTS:
            continue
        if frag in id_to_url:
            mapping[frag] = id_to_url[frag]
    # kotwice sekcji i nagran zawsze, nawet jesli nikt do nich nie linkowal
    for page in CONTENT_PAGES:
        mapping[page["id"]] = id_to_url[page["id"]]
    for rec in RECORDINGS:
        mapping[rec["id"]] = id_to_url[rec["id"]]
    return mapping


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
    for page in CONTENT_PAGES + RECORDINGS:
        tag = soup.find(id=page["id"])
        expect(tag is not None, "brak sekcji #%s w zrodle" % page["id"])
        url = BASE + "/" + page["slug"] + "/"
        for inner in tag.find_all(attrs={"id": True}):
            id_to_url[inner["id"]] = url + "#" + inner["id"]
        id_to_url[page["id"]] = url
    return id_to_url


# --------------------------------------------------------------------------
# Szybkosc: CSS i duze skrypty do plikow zewnetrznych (cache przegladarki)
# --------------------------------------------------------------------------

ASSET_DIR = "assets"
_ASSETS = {}


def _store_asset(content, suffix):
    """Zapisuje tresc jako plik z odciskiem w nazwie; zwraca adres.

    Ten sam arkusz stylow i te same skrypty maja na kazdej stronie identyczna
    tresc, wiec powstaje jeden plik, ktory przegladarka pobiera RAZ i trzyma
    w pamieci podrecznej dla calej witryny.
    """
    key = (suffix, content)
    if key in _ASSETS:
        return _ASSETS[key]
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()[:10]
    rel = "%s/site-%s.%s" % (ASSET_DIR, digest, suffix)
    out = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(content)
    _ASSETS[key] = BASE + "/" + rel
    return _ASSETS[key]


# Skrypty, ktore MUSZA zostac w kodzie strony (wykonuja sie przed renderowaniem
# albo przekierowuja) — nie wolno ich odkladac atrybutem defer.
INLINE_ONLY_JS_MARKS = ("location.replace", "setLanguage")
EXTERNALIZE_JS_MIN = 1500
EXTERNALIZE_CSS_MIN = 4000


def minify_css(css):
    """Zachowawcza minifikacja arkusza stylow.

    Usuwa komentarze i zbedne biale znaki, nie ruszajac niczego wewnatrz
    cudzyslowow ani wewnatrz nawiasow (calc(), media queries, rgba()) — tam
    spacje maja znaczenie. Nie zmienia ani jednej wlasnosci i ani jednego
    selektora; przy niezgodnosci licznikow build przerywa prace.
    """
    out = []
    i = 0
    n = len(css)
    depth_paren = 0
    while i < n:
        ch = css[i]
        # komentarze
        if ch == "/" and css.startswith("/*", i):
            end = css.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        # napisy w cudzyslowach — kopiujemy bez zmian
        if ch in "\"'":
            quote = ch
            j = i + 1
            while j < n:
                if css[j] == "\\":
                    j += 2
                    continue
                if css[j] == quote:
                    j += 1
                    break
                j += 1
            out.append(css[i:j])
            i = j
            continue
        if ch == "(":
            depth_paren += 1
            out.append(ch)
            i += 1
            continue
        if ch == ")":
            depth_paren = max(0, depth_paren - 1)
            out.append(ch)
            i += 1
            continue
        if ch in " \t\r\n\f":
            j = i
            while j < n and css[j] in " \t\r\n\f":
                j += 1
            nxt = css[j] if j < n else ""
            prev = out[-1][-1] if out and out[-1] else ""
            if depth_paren:
                # wewnatrz nawiasow spacja moze byc znaczaca (calc)
                out.append(" ")
            elif nxt in "{},;>" or prev in "{},;:>" or nxt == "":
                pass
            else:
                out.append(" ")
            i = j
            continue
        out.append(ch)
        i += 1

    text = "".join(out)
    text = re.sub(r";+\}", "}", text)
    text = re.sub(r"\}\s*", "}", text)
    return text.strip()


def _css_shape(css):
    """Odcisk struktury arkusza: liczba blokow i deklaracji (do kontroli)."""
    stripped = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    stripped = re.sub(r"([\"'])(?:\\.|(?!\1).)*\1", '""', stripped, flags=re.S)
    return (stripped.count("{"), stripped.count("}"),
            len([d for d in re.split(r"[;{}]", stripped) if ":" in d]))


def externalize_assets(soup):
    for style in list(soup.find_all("style")):
        css = style.string or ""
        if len(css) < EXTERNALIZE_CSS_MIN:
            continue
        small = minify_css(css)
        expect(_css_shape(small) == _css_shape(css),
               "minifikacja CSS zmienila strukture arkusza: %s vs %s"
               % (_css_shape(small), _css_shape(css)))
        css = small
        link = soup.new_tag("link", href=_store_asset(css, "css"))
        link["rel"] = "stylesheet"
        style.replace_with(link)

    for script in list(soup.find_all("script")):
        if script.get("src") or script.get("type") == "application/ld+json":
            continue
        code = script.string or ""
        if len(code) < EXTERNALIZE_JS_MIN:
            continue
        if any(mark in code for mark in INLINE_ONLY_JS_MARKS):
            continue
        new = soup.new_tag("script", src=_store_asset(code, "js"))
        new["defer"] = ""
        script.replace_with(new)


# Fonty: hostowane lokalnie (assets/fonts/), zero zapytan do Google.
FONTS_CSS = "assets/fonts/fonts.css"


def localize_fonts(soup):
    """Usuwa odwolania do fonts.googleapis.com / fonts.gstatic.com.

    Arkusz Google Fonts blokuje renderowanie strony i wymaga dwoch dodatkowych
    polaczen do obcego serwera. Te same fonty (Inter, Source Serif 4 — licencja
    OFL) leza teraz w repozytorium; pobiera je `tools/pobierz_fonty.py`.
    """
    removed = 0
    for link in list(soup.find_all("link", href=True)):
        if "fonts.googleapis.com" in link["href"] or "fonts.gstatic.com" in link["href"]:
            link.decompose()
            removed += 1
    if not soup.find("link", href=BASE + "/" + FONTS_CSS):
        local = soup.new_tag("link", href=BASE + "/" + FONTS_CSS)
        local["rel"] = "stylesheet"
        anchor = soup.head.find("link", attrs={"rel": ["canonical"]}) or soup.head
        if anchor is soup.head:
            soup.head.append(local)
        else:
            anchor.insert_before(local)
    return removed


def local_thumb_for(video_id):
    rel = "docs/yt-%s.jpg" % video_id
    return rel if os.path.exists(os.path.join(ROOT, rel)) else None


def youtube_facade(soup, lang):
    """Osadzony odtwarzacz YouTube -> zaslona z przyciskiem odtwarzania.

    Przed kliknieciem strona nie kontaktuje sie z YouTube w ogole: zaden skrypt
    firmy trzeciej, zadne ciasteczko, zadne ~600 KB odtwarzacza na film.
    Gdy w `docs/` jest lokalna miniatura (`docs/yt-<id>.jpg`), zaslona ja
    pokazuje; w przeciwnym razie jest ciemnym kafelkiem z tytulem — nadal bez
    zadnego zapytania na zewnatrz. Po kliknieciu film startuje normalnie.
    """
    label, hint = YT_FACADE_LABEL[lang]
    replaced = 0
    for frame in list(soup.find_all("iframe")):
        src = (frame.get("src") or "")
        if YT_EMBED_MARK not in src:
            continue
        title = (frame.get("title") or "").strip()
        video_id = src.split("/embed/", 1)[1].split("?", 1)[0].strip("/")
        thumb = local_thumb_for(video_id)

        btn = soup.new_tag("button", type="button")
        btn["class"] = ["yt-facade"] if thumb else ["yt-facade", "yt-facade-plain"]
        btn["data-yt"] = src
        btn["aria-label"] = "%s%s" % (label, (": " + title) if title else "")
        if thumb:
            img = soup.new_tag("img", src=thumb, alt="")
            img["width"] = "960"
            img["height"] = "540"
            img["loading"] = "lazy"
            img["decoding"] = "async"
            btn.append(img)
        play = soup.new_tag("span")
        play["class"] = ["yt-play"]
        play["aria-hidden"] = "true"
        btn.append(play)
        caption = soup.new_tag("span")
        caption["class"] = ["yt-caption"]
        caption.string = title or ("%s — %s" % (label, hint))
        btn.append(caption)

        wrapper = frame.parent
        frame.replace_with(btn)
        if wrapper is not None and wrapper.name == "div" and \
                "padding-bottom:56.25%" in (wrapper.get("style") or ""):
            wrapper.replace_with(btn)
        replaced += 1

    if replaced:
        script = soup.new_tag("script")
        script.string = YT_FACADE_JS
        soup.body.append(script)


def speed_polish(soup):
    """Drobne poprawki wydajnosci: leniwe obrazy i asynchroniczne dekodowanie."""
    for img in soup.find_all("img"):
        if not img.get("loading"):
            img["loading"] = "lazy"
        if not img.get("decoding"):
            img["decoding"] = "async"


def finish(soup, path):
    youtube_facade(soup, soup.html.get("lang", "pl"))
    localize_fonts(soup)
    speed_polish(soup)
    externalize_assets(soup)
    absolutize_assets(soup)
    logo = soup.find("a", class_="header-logo")
    if logo is not None:
        logo["href"] = BASE + "/"
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out) or ROOT, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(str(soup))
    return out


def build_language_page(raw, lang, id_to_url, anchor_map=None):
    soup = prepared_soup(raw, lang)
    rewrite_lang_switcher(soup, lang)
    transform_scripts(soup)
    append_css(soup)

    title, description = LANG_META[lang]
    page_url = LANG_URL[lang]
    set_head(soup, lang=lang, title=title, description=description, page_url=page_url,
             hreflang_cluster=True, keep_faq=(lang == "pl"))

    if lang == "pl":
        # ODTLUSZCZENIE: na stronie glownej zostaje hero + sekcja #home-hub.
        # Cala pozostala tresc jest na podstronach (patrz CONTENT_PAGES,
        # RECORDINGS) — z home jest wylacznie USUWANA, nigdy skracana.
        hub = soup.find(id="home-hub")
        expect(hub is not None, "brak sekcji #home-hub w zrodle")
        for sec in soup.find_all("section"):
            classes = set(sec.get("class") or [])
            if "hero" in classes or sec.get("id") in HOME_KEEP_SECTION_IDS:
                continue
            sec.decompose()
        strip_inpage_navs(soup)
        update_graph_for_language(soup, lang, page_url, id_to_url)
        rewrite_anchors(soup, id_to_url=id_to_url, always_remap=True)
        if anchor_map:
            install_anchor_redirect(soup, anchor_map)
    else:
        # Strony jezykowe maja nadal pelna tresc jednej strony —
        # zmienia sie wylacznie nawigacja (szesc zakladek).
        hub = soup.find(id="home-hub")
        if hub is not None:
            hub.decompose()
        update_graph_for_language(soup, lang, page_url, {})

    install_nav(soup, lang, current="sprawa")
    install_footer_links(soup, lang)

    path = "index.html" if lang == "pl" else "%s/index.html" % lang
    return finish(soup, path)


def page_chrome(raw, page_title, page_desc, page_url, nav_current):
    """Wspolny szkielet podstrony PL: naglowek, menu, pusty <main>, stopka."""
    soup = prepared_soup(raw, "pl")
    rewrite_lang_switcher(soup, "pl")
    transform_scripts(soup)
    append_css(soup)
    set_head(soup, lang="pl", title=page_title, description=page_desc,
             page_url=page_url, hreflang_cluster=False, keep_faq=False)

    hero = soup.find("section", class_="hero")
    if hero is not None:
        hero.decompose()
    hub = soup.find(id="home-hub")
    if hub is not None:
        hub.decompose()

    main = soup.find("main")
    expect(main is not None, "brak <main>")
    return soup, main


def put_ld(soup, data):
    for script in ld_scripts(soup):
        script.decompose()
    ld = soup.new_tag("script", attrs={"type": "application/ld+json"})
    ld.string = "\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    soup.head.append(ld)


def build_content_page(raw, page, id_to_url, extra_top=None, extra_bottom=None):
    """Podstrona z trescia przeniesiona ze strony glownej — HTML kopiowany 1:1."""
    page_url = SITE + "/" + page["slug"] + "/"
    soup, main = page_chrome(raw, page["title"], page["desc"], page_url,
                             GROUP_OF_SLUG.get(page["slug"]))

    section_tag = soup.find(id=page["id"])
    expect(section_tag is not None, "brak sekcji #%s" % page["id"])
    section_tag.extract()

    for stray in soup.find_all("section"):
        stray.decompose()

    strip_inpage_navs(section_tag)
    headline = promote_first_heading(section_tag) or page["short"]

    main.clear()
    group = GROUP_OF_SLUG.get(page["slug"])
    main.append(build_breadcrumb_for(soup, page["short"], group))
    for node in (extra_top or []):
        main.append(node)
    main.append(section_tag)
    for node in (extra_bottom or []):
        main.append(node)
    main.append(build_related(soup, page["slug"]))

    put_ld(soup, section_ld(page, headline))
    install_nav(soup, "pl", current=nav_current_for(page["slug"]))
    install_footer_links(soup, "pl")
    rewrite_anchors(soup, id_to_url=id_to_url)
    return finish(soup, "%s/index.html" % page["slug"])


def nav_current_for(slug):
    group = GROUP_OF_SLUG.get(slug)
    if group == "sprawa":
        return "sprawa"
    if group in ("nagrania", "postepowania", "instytucje", "o-mnie", "dokumenty"):
        return group
    return None


def build_recording_page(raw, rec, id_to_url):
    """Podstrona jednego nagrania: metryczka, nota o numeracji, nawigacja."""
    soup_tmp = BeautifulSoup("<div></div>", "html.parser")

    meta = soup_tmp.new_tag("ul")
    meta["class"] = ["rec-meta"]
    for label, value in (("Data", rec["date"]), ("Uczestnicy", rec["people"]),
                         ("Czas trwania", rec["length"])):
        li = soup_tmp.new_tag("li")
        strong = soup_tmp.new_tag("strong")
        strong.string = label + ": "
        li.append(strong)
        li.append(value)
        meta.append(li)

    note = soup_tmp.new_tag("p")
    note["class"] = ["rec-numbering"]
    note.append(NUMBERING_NOTE_TEXT % (rec["n"], rec["analiza"]) + " ")
    link = soup_tmp.new_tag("a", href=NUMBERING_NOTE_URL)
    link.string = "Nota o numeracji nagrań (20 sierpnia 2026 r.)"
    note.append(link)

    idx = [r["n"] for r in RECORDINGS].index(rec["n"])
    prevnext = soup_tmp.new_tag("nav")
    prevnext["class"] = ["rec-prevnext"]
    prevnext["aria-label"] = "Nawigacja między nagraniami"
    if idx > 0:
        before = RECORDINGS[idx - 1]
        a = soup_tmp.new_tag("a", href=BASE + "/" + before["slug"] + "/")
        a.string = "← poprzednie: %s" % before["short"]
        prevnext.append(a)
    hub = soup_tmp.new_tag("a", href=BASE + "/nagrania/")
    hub.string = "Wszystkie nagrania"
    prevnext.append(hub)
    if idx < len(RECORDINGS) - 1:
        after = RECORDINGS[idx + 1]
        a = soup_tmp.new_tag("a", href=BASE + "/" + after["slug"] + "/")
        a.string = "następne: %s →" % after["short"]
        prevnext.append(a)

    return build_content_page(raw, rec, id_to_url,
                             extra_top=[meta, note],
                             extra_bottom=[prevnext])


def hub_items(hub):
    """Lista (url, tytul, opis) podstron danego dzialu."""
    out = []
    if hub["slug"] == "nagrania":
        for rec in RECORDINGS:
            out.append((BASE + "/" + rec["slug"] + "/", rec["short"], rec["desc"]))
        return out
    for slug in hub["items"]:
        page = PAGE_BY_SLUG[slug]
        out.append((BASE + "/" + slug + "/", page["short"], page["desc"]))
    return out


def build_hub_page(raw, hub, id_to_url):
    """Strona-hub dzialu: wylacznie pionowa lista podstron (bez tresci)."""
    page_url = SITE + "/" + hub["slug"] + "/"
    soup, main = page_chrome(raw, hub["title"], hub["desc"], page_url, hub["slug"])

    for stray in soup.find_all("section"):
        stray.decompose()

    main.clear()
    wrap = soup.new_tag("div")
    wrap["class"] = ["hub-page"]
    wrap.append(build_breadcrumb_for(soup, hub["short"]))
    h1 = soup.new_tag("h1")
    h1.string = hub["h1"]
    wrap.append(h1)
    intro = soup.new_tag("p")
    intro["class"] = ["hub-intro"]
    intro.string = hub["intro"]
    wrap.append(intro)

    ul = soup.new_tag("ul")
    ul["class"] = ["hub-list"]
    for href, label, desc in hub_items(hub):
        li = soup.new_tag("li")
        a = soup.new_tag("a", href=href)
        a["class"] = ["hub-list-title"]
        a.string = label
        li.append(a)
        p = soup.new_tag("p")
        p.string = desc
        li.append(p)
        ul.append(li)
    wrap.append(ul)

    if hub["slug"] == "nagrania":
        note = soup.new_tag("p")
        note["class"] = ["rec-numbering"]
        note.append("Witryna numeruje nagrania 1–7, a dokument "
                    "analiza_nagran_audio_kompletna — 1–10. Żadnej numeracji nie "
                    "zmieniono; tabela przeliczenia: ")
        link = soup.new_tag("a", href=NUMBERING_NOTE_URL)
        link.string = "nota o numeracji z 20 sierpnia 2026 r."
        note.append(link)
        wrap.append(note)

    main.append(wrap)

    put_ld(soup, section_ld({"slug": hub["slug"], "desc": hub["desc"],
                             "short": hub["short"]}, hub["h1"]))
    install_nav(soup, "pl", current=hub["slug"])
    install_footer_links(soup, "pl")
    rewrite_anchors(soup, id_to_url=id_to_url)
    return finish(soup, "%s/index.html" % hub["slug"])


def build_skorowidz_page(raw, lang, id_to_url):
    """Pelna lista odnosnikow z dawnego drugiego rzedu zakladek (nav.sub-nav).

    Rzad zakladek zostal usuniety z chrome witryny, ale ani jeden odnosnik
    nie zniknal — wszystkie sa tutaj, w pionowej liscie.
    """
    title, desc, h1_text, intro_text = SKOROWIDZ_META[lang]
    slug = "skorowidz" if lang == "pl" else "%s/skorowidz" % lang
    page_url = SITE + "/" + slug + "/"

    soup = prepared_soup(raw, lang)
    rewrite_lang_switcher(soup, lang)
    transform_scripts(soup)
    append_css(soup)
    set_head(soup, lang=lang, title=title, description=desc, page_url=page_url,
             hreflang_cluster=False, keep_faq=False)

    subnav = soup.find("nav", class_="sub-nav")
    expect(subnav is not None, "brak nav.sub-nav w zrodle (%s)" % lang)
    subnav.extract()

    hero = soup.find("section", class_="hero")
    if hero is not None:
        hero.decompose()
    for stray in soup.find_all("section"):
        stray.decompose()

    main = soup.find("main")
    expect(main is not None, "brak <main>")
    main.clear()

    wrap = soup.new_tag("div")
    wrap["class"] = ["hub-page", "skorowidz"]
    wrap.append(build_breadcrumb_for(soup, h1_text))
    h1 = soup.new_tag("h1")
    h1.string = h1_text
    wrap.append(h1)
    intro = soup.new_tag("p")
    intro["class"] = ["hub-intro"]
    intro.string = intro_text
    wrap.append(intro)

    for tab in subnav.select("div.sub-nav-tab"):
        head_link = tab.find("a", class_="sub-nav-link")
        if head_link is None:
            continue
        h2 = soup.new_tag("h2")
        h2.string = head_link.get_text(" ", strip=True)
        wrap.append(h2)
        ul = soup.new_tag("ul")
        for node in tab.select(".sub-nav-dropdown > *"):
            classes = set(node.get("class") or [])
            if "sub-nav-dropdown-title" in classes:
                if ul.find("li") is not None:
                    wrap.append(ul)
                    ul = soup.new_tag("ul")
                h3 = soup.new_tag("h3")
                h3.string = node.get_text(" ", strip=True)
                wrap.append(h3)
                continue
            if node.name == "a":
                li = soup.new_tag("li")
                a = soup.new_tag("a", href=node.get("href", "#"))
                if node.get("target"):
                    a["target"] = node["target"]
                    a["rel"] = "noopener noreferrer"
                a.string = node.get_text(" ", strip=True)
                li.append(a)
                ul.append(li)
        if ul.find("li") is not None:
            wrap.append(ul)

    main.append(wrap)

    put_ld(soup, section_ld({"slug": slug, "desc": desc, "short": h1_text}, h1_text))
    install_nav(soup, lang, current=None)
    install_footer_links(soup, lang)
    rewrite_anchors(soup, id_to_url=id_to_url, always_remap=True)
    return finish(soup, "%s/index.html" % slug)


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

    for slug, priority in sitemap_slugs():
        lines.append("  <url>")
        lines.append("    <loc>%s/%s/</loc>" % (SITE, slug))
        lines.append("    <lastmod>%s</lastmod>" % BUILD_DATE)
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>%s</priority>" % priority)
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


def sitemap_slugs():
    """Slugi wszystkich generowanych podstron + priorytety (kolejnosc = sitemap)."""
    out = [(h["slug"], "0.9") for h in HUBS]
    out += [(p["slug"], "0.7") for p in CONTENT_PAGES]
    out += [(r["slug"], "0.7") for r in RECORDINGS]
    out += [("skorowidz", "0.5")]
    out += [("%s/skorowidz" % l, "0.4") for l in LANGS if l != "pl"]
    return out


def build_404():
    items = "\n".join(
        '<li><a href="%s/%s/">%s</a></li>' % (BASE, h["slug"], h["short"])
        for h in HUBS)
    items += "\n" + "\n".join(
        '<li><a href="%s/%s/">%s</a></li>' % (BASE, s["slug"], s["short"])
        for s in CONTENT_PAGES)
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

def all_generated_paths():
    paths = ["index.html"] + ["%s/index.html" % l for l in LANGS if l != "pl"]
    paths += ["%s/index.html" % slug for slug, _p in sitemap_slugs()]
    paths += ["404.html"]
    return paths


def check_inline_js(paths=None):
    """Kazdy skrypt inline musi byc poprawnym JavaScriptem.

    Kontrola dodana 20 sierpnia 2026 r. po wykryciu, ze wstawiany automatycznie
    straznik null psul skladnie glownego skryptu witryny. Wymaga polecenia
    `node`; jesli go nie ma, kontrola jest pomijana z komunikatem.
    """
    node = shutil.which("node")
    if not node:
        print("  (pomijam kontrole skladni JS — brak polecenia `node`)")
        return
    import subprocess
    import tempfile
    problems = []
    for rel in (paths or all_generated_paths()):
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            soup = BeautifulSoup(fh.read(), "html.parser")
        for i, script in enumerate(soup.find_all("script")):
            if script.get("src") or script.get("type") == "application/ld+json":
                continue
            code = script.string or ""
            if not code.strip():
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                             encoding="utf-8") as tmp:
                tmp.write(code)
                name = tmp.name
            res = subprocess.run([node, "--check", name],
                                 capture_output=True, text=True)
            os.unlink(name)
            if res.returncode:
                first = (res.stderr.strip().splitlines() or ["?"])[0]
                problems.append("%s: skrypt #%d — %s" % (rel, i, first))
    expect(not problems,
           "niepoprawny JavaScript (%d): %s" % (len(problems), "; ".join(problems[:6])))


def check_no_broken_links():
    """Kontrola koncowa: kazdy lokalny odnosnik ma istniejacy plik, kazda
    kotwica #... ma odpowiadajace id na tej samej stronie."""
    problems = []
    for rel in all_generated_paths():
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as fh:
            soup = BeautifulSoup(fh.read(), "html.parser")
        ids = {t["id"] for t in soup.find_all(attrs={"id": True})}
        for tag in soup.find_all(True):
            for attr in ("href", "src", "poster"):
                value = tag.get(attr)
                if not isinstance(value, str):
                    continue
                value = value.strip()
                if value.startswith("#"):
                    frag = value[1:]
                    if frag not in NATIVE_FRAGMENTS and frag not in ids:
                        problems.append("%s: osierocona kotwica #%s" % (rel, frag))
                    continue
                if not value.startswith(BASE + "/") or value.startswith("//"):
                    continue
                target = unquote(urlparse(value).path)[len(BASE):].lstrip("/")
                if target == "" or target.endswith("/"):
                    target += "index.html"
                if not os.path.exists(os.path.join(ROOT, target)):
                    problems.append("%s: brak pliku %s" % (rel, target))
    problems = sorted(set(problems))
    expect(not problems,
           "zerwane odnosniki (%d): %s" % (len(problems), "; ".join(problems[:12])))


def main():
    # Czyscimy tylko pliki generowane (site-*.css / site-*.js).
    # assets/fonts/ zostaje — to zasoby staler, pobierane osobno.
    assets = os.path.join(ROOT, ASSET_DIR)
    if os.path.isdir(assets):
        for name in os.listdir(assets):
            if name.startswith("site-"):
                os.unlink(os.path.join(assets, name))

    raw = load_source()
    id_to_url = collect_section_id_map(raw)
    anchor_map = collect_old_anchors(raw, id_to_url)

    written = []
    written.append(build_language_page(raw, "pl", id_to_url, anchor_map))
    for lang in LANGS:
        if lang == "pl":
            continue
        written.append(build_language_page(raw, lang, id_to_url))
    for hub in HUBS:
        written.append(build_hub_page(raw, hub, id_to_url))
    for page in CONTENT_PAGES:
        written.append(build_content_page(raw, page, id_to_url))
    for rec in RECORDINGS:
        written.append(build_recording_page(raw, rec, id_to_url))
    for lang in LANGS:
        written.append(build_skorowidz_page(raw, lang, id_to_url))
    written.append(build_sitemap())
    written.append(build_404())
    check_robots()
    check_no_broken_links()
    check_inline_js()

    print("Zbudowano (%s):" % BUILD_DATE)
    for path in written:
        rel = os.path.relpath(path, ROOT)
        print("  %-42s %8.1f KB" % (rel, os.path.getsize(path) / 1024))
    print("  Kotwic przekierowanych na nowe adresy: %d" % len(anchor_map))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print("BLAD BUDOWANIA: %s" % exc, file=sys.stderr)
        sys.exit(1)
