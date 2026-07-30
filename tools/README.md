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
