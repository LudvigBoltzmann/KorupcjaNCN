# Inwentaryzacja stanu PRZED odtłuszczeniem

**Data pomiaru:** 20 sierpnia 2026 r.
**Repozytorium:** LudvigBoltzmann/KorupcjaNCN
**Gałąź robocza:** `odtluszczenie-2026-08`
**Commit stanu początkowego:** `40dc877` (gałąź `main`, nietknięta)
**Mierzony plik:** `index.html` (strona główna PL, wygenerowana z `src/index.src.html`)

---

## 1. Jak liczone są znaki

Zliczam **znaki widocznej treści** strony (tekst z `<body>` po usunięciu `<style>`,
`<script>` i `<noscript>`, z normalizacją białych znaków). To jedyna miara, która
opisuje, ile czytelnik ma przed sobą tekstu. Podaję dodatkowo wagę pliku i liczbę
znaków HTML, ale należy pamiętać, że ok. 88 KB każdej strony to wspólny arkusz
stylów wklejony w `<style>` i skrypty — one nie są treścią i nie zmieniają się
przy odtłuszczaniu.

## 2. Liczby przed zmianami

| Miara | Wartość |
| --- | --- |
| Waga pliku `index.html` | 255 779 B (249,8 KB) |
| Znaki HTML (cały plik) | 251 773 |
| **Znaki widocznej treści** | **56 668** |
| Słowa widocznej treści | 8 323 |
| Sekcji `<section>` na home | 26 |
| Drugi rząd zakładek (`nav.sub-nav`) | 5 369 znaków, 136 odnośników |

Ustalenie źródła prawdy: treść edytuje się **wyłącznie** w `src/index.src.html`
(1,15 MB, pięć wersji językowych w blokach `.lang-block`). `index.html` oraz
wszystkie podstrony są generowane przez `tools/build.py`; ręczna edycja pliku
wynikowego zostałaby nadpisana przy najbliższym buildzie. Potwierdzone: build
uruchomiony na czystym repozytorium odtworzył wszystkie pliki bez żadnej różnicy.

## 3. Sekcje strony głównej w kolejności występowania

Kolumna „Pełna treść na podstronie?" opisuje stan **przed** zmianami.

| # | Sekcja (`id`) | Nagłówek | Znaki | Słowa | Pełna treść na podstronie? |
| --- | --- | --- | --- | --- | --- |
| 1 | (hero) | Dr Witold Kilarski | 302 | 45 | NIE (element wspólny witryny) |
| 2 | `case` | Korupcja w Narodowym Centrum Nauki | 2 353 | 319 | NIE |
| 3 | `prokuratura-ochonska` | Odmowa wszczęcia śledztwa przez prokuraturę | 542 | 70 | TAK — /prokuratura/ |
| 4 | `interview` | Rozmowa z osobą NN (nagranie 1) | 4 872 | 733 | NIE |
| 5 | `interview-3-4` | Rozmowa 2 — 2 czerwca 2020 | 3 970 | 567 | NIE |
| 6 | `interview-4` | Rozmowa 3 — 4 czerwca 2020 | 3 594 | 553 | NIE |
| 7 | `rec-4` | Nagranie 4 — 10 października 2020 | 2 505 | 360 | NIE |
| 8 | `rec-5a` | Nagranie 5 — 20 marca 2021 (A i B) | 3 472 | 511 | NIE |
| 9 | `rec-6` | Nagranie 6 — telefon osoby NN | 3 900 | 564 | NIE |
| 10 | `rec-7` | Nagranie 7 — 30 września 2021 | 5 257 | 799 | NIE |
| 11 | `courts` | Ukarany sygnalista, nie skorumpowani urzędnicy | 892 | 124 | TAK — /sprawy-sadowe/ |
| 12 | `documents` | Kluczowe dowody | 785 | 101 | TAK — /dokumenty/ |
| 13 | `uj-inaction` | Bezczynność Uniwersytetu Jagiellońskiego | 1 029 | 145 | TAK — /bezczynnosc-uj/ |
| 14 | `sprawa-blocki-babik-liana` | Błocki, Babik, Liana | 1 143 | 153 | TAK — /blocki-babik-liana/ |
| 15 | `blocki-cyngiel` | WUM odcina mnie po piśmie Dyrektora NCN | 2 450 | 356 | NIE |
| 16 | `mudelsee` | Maszynowe recenzje — sprawa Mudelsee | 982 | 127 | TAK — /maszynowe-recenzje-ncn/ |
| 17 | `timeline` | Kluczowe daty (chronologia) | 1 194 | 168 | NIE |
| 18 | `about` | Dr Witold Kilarski — o mnie i CV | 1 017 | 144 | NIE |
| 19 | `wniosek-kontrola-ncn` | Wniosek o kontrolę NCN i UJ | 1 613 | 233 | TAK — /wniosek-o-kontrole-ncn/ |
| 20 | `list-otwarty` | List otwarty do Premiera i Ministra | 1 885 | 242 | NIE |
| 21 | `ukraina` | Pomoc Ukraińcom | 1 835 | 292 | NIE |
| 22 | `kulturowe-analogie` | Kulturowe analogie | 2 198 | 364 | NIE |
| 23 | `wyrok-kafkowski` | Wyrok w trybie kafkowskim (I C 1671/22) | 865 | 141 | TAK — /wyrok-kafkowski/ |
| 24 | `komornik` | Sprawa komornika Km 834/26 | 1 531 | 222 | TAK — /sprawa-komornika/ |
| 25 | `comments` | Dyskusja | 228 | 31 | NIE |
| 26 | `sprostowania` | Sprostowania i korekty | 370 | 52 | TAK — /sprostowania/ |

Suma znaków sekcji: 50 784. Pozostałe ok. 5 900 znaków to nagłówek strony,
drugi rząd zakładek (`nav.sub-nav`), wewnątrzstronowe rzędy odnośników
(`.section-nav`, `.section-jumpnav`) i stopka.

**Uwaga do kolumny „na podstronie":** dziesięć sekcji miało już wcześniej własne
podstrony, ale na stronie głównej pozostawał ich **skrót** (etykieta, nagłówek
i do trzech pierwszych akapitów) — pełna treść była na podstronie. Dla tych
sekcji odtłuszczenie polega na usunięciu skrótu z home (treść zostaje bez zmian
na podstronie). Dla sekcji oznaczonych NIE najpierw powstała podstrona
z **pełną, skopiowaną 1:1** treścią, a dopiero potem treść zniknęła z home.

## 4. Kopia stanu początkowego i cofanie zmian

Kopie zapasowe w katalogu `backup/`:

- `backup/index.src.html.orig` — plik źródłowy przed zmianami,
- `backup/index.html.orig` — strona główna przed zmianami,
- `backup/build.py.orig` — generator przed zmianami,
- `backup/sitemap.xml.orig` — mapa witryny przed zmianami.

Cofnięcie **wszystkich** zmian jednym poleceniem:

```bash
bash raport/przywroc-stan-przed.sh
```

Skrypt przywraca całe repozytorium do commita `40dc877` (stan przed
odtłuszczeniem) i usuwa pliki dodane po tej dacie. Gałąź `main` nie była
w ogóle dotykana, więc alternatywnie wystarczy usunąć gałąź roboczą:

```bash
git checkout main && git branch -D odtluszczenie-2026-08
```
