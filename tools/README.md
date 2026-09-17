# tools — generowanie stron witryny

Witryna jest generowana z **jednego** pliku źródłowego: `src/index.src.html`
(pięciojęzyczny monolit z blokami `<div class="lang-block" data-lang="…">`).

## Jak zbudować

```bash
pip install beautifulsoup4      # jedyna zależność, parser: html.parser
python3 tools/build.py          # generuje wszystkie pliki
python3 tools/verify.py         # raport kontrolny (kod wyjścia 0 = czysto)
```

`tools/build.py` tworzy:

| plik | zawartość |
| --- | --- |
| `index.html` | PL — hub, skróty ośmiu wydzielonych sekcji |
| `en/`, `fr/`, `de/`, `uk/` `index.html` | pełna treść w danym języku |
| `sprawa-komornika/`, `wyrok-kafkowski/`, `bezczynnosc-uj/`, `blocki-babik-liana/`, `maszynowe-recenzje-ncn/`, `dokumenty/`, `sprawy-sadowe/`, `prokuratura/` | strony sekcyjne PL |
| `sitemap.xml` | 13 URL-i + klaster hreflang |
| `404.html` | strona błędu (`noindex`) |

## Zasady

- **Treść edytuj WYŁĄCZNIE w `src/index.src.html`.** Wszystkie pozostałe
  pliki HTML w korzeniu i podkatalogach są generowane i każdy build je
  nadpisuje — ręczne zmiany zostaną utracone.
- Po każdej edycji źródła uruchom `python3 tools/build.py`. Alternatywnie
  wystarczy wypchnąć zmianę w `src/**` lub `tools/**` na gałąź `main` —
  workflow `.github/workflows/build-pages.yml` zbuduje i zacommituje
  wygenerowane pliki (z `[skip ci]`).
- Nie używaj parsera `lxml` — przebudowuje markup. Skrypt korzysta
  z `html.parser`.
- Metadane (title, description, slugi sekcji) są w stałych na początku
  `tools/build.py`: `LANG_META` i `SECTIONS`.
- Build jest asertywny: jeśli oczekiwany fragment HTML/JS nie zostanie
  znaleziony w źródle, skrypt przerywa pracę z komunikatem zamiast po cichu
  wygenerować niepełną stronę.

## Co powstaje po odtłuszczeniu (2026-08-20)

| plik / katalog | zawartość |
| --- | --- |
| `index.html` | PL — strona główna: nagłówek, streszczenie, cytat, 6 kafli, skrócona chronologia, nota o autorze |
| `en/`, `fr/`, `de/`, `uk/` | pełna treść w danym języku (jedna strona) |
| `nagrania/`, `postepowania/`, `instytucje/`, `o-mnie/` | strony-huby czterech działów menu |
| `nagrania/1/` … `nagrania/7/` | po jednej podstronie na nagranie |
| 18 podstron PL z treścią | `CONTENT_PAGES` w `tools/build.py` |
| `skorowidz/` + `en|fr|de|uk/skorowidz/` | pełna lista odnośników z dawnego drugiego rzędu zakładek |
| `assets/site-*.css`, `assets/site-*.js` | wspólny arkusz stylów i skrypty (nazwa z odciskiem treści → cache) |
| `assets/fonts/` | fonty hostowane lokalnie + `fonts.css` (skrypt `tools/pobierz_fonty.py`) |

## Narzędzia pomocnicze

```bash
python3 tools/measure_home.py          # objętość strony głównej (znaki, słowa, waga)
python3 tools/sprawdz_adresy.py        # kody odpowiedzi wszystkich adresów (serwer lokalny)
python3 tools/pobierz_fonty.py         # tylko gdy zmienia się zestaw fontów
bash raport/przywroc-stan-przed.sh     # cofnięcie wszystkich zmian odtłuszczenia
```

## Zasady dodane 20 sierpnia 2026

- Build **przerywa pracę**, gdy: jakiś odnośnik lokalny nie ma pliku, jakaś kotwica
  `#...` nie ma celu na stronie, albo któryś skrypt inline nie jest poprawnym
  JavaScriptem (`node --check`).
- Menu ma **dokładnie sześć zakładek** (`NAV_TABS`); nie ma drugiego rzędu zakładek.
- Osadzone odtwarzacze YouTube są zamieniane na zasłonę z przyciskiem — do
  kliknięcia strona nie wysyła żadnego zapytania do YouTube.
- Fonty są hostowane lokalnie; w `<head>` nie ma odwołań do fonts.googleapis.com.
