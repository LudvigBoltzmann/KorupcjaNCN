# Raport końcowy — odtłuszczenie strony głównej witekkilarski.org

**Data:** 20 sierpnia 2026 r.
**Repozytorium:** LudvigBoltzmann/KorupcjaNCN
**Gałąź robocza:** `odtluszczenie-2026-08` — **`main` nietknięty, nic nie scalono**
**Wykonawca zlecenia:** asystent AI, na zlecenie dr. Witolda Kilarskiego
**Kontakt autora witryny:** witek.kilarski@gmail.com, +48 782 473 130

---

## 1. Liczby przed i po

| Miara | Przed | Po | Zmiana |
| --- | --- | --- | --- |
| **Znaki widocznej treści strony głównej** | 56 668 | 6 632 | **−88,3%** |
| Słowa widocznej treści | 8 323 | 945 | −88,6% |
| Liczba sekcji `<section>` na home | 26 | 2 (hero + streszczenie) | −24 |
| Znaki HTML całego pliku | 251 773 | 146 066 | −42,0% |
| Waga pliku `index.html` | 255 779 B (249,8 KB) | 147 140 B (143,7 KB) | −42,5% |

**Kryterium odbioru „spadek ≥ 80% liczby znaków (cel 85%)" — spełnione: 88,3%.**

Wyjaśnienie różnicy między dwiema miarami: w każdej stronie witryny siedzi
wklejony arkusz stylów (ok. 88 KB) i skrypty (ok. 17 KB). To nie jest treść i nie
da się tego usunąć odtłuszczaniem — dlatego spadek wagi pliku (42%) jest mniejszy
niż spadek treści (88%). Propozycję wyniesienia stylów do osobnego pliku
zapisałem w punkcie 5 (Twoja decyzja).

Strona główna po zmianach zawiera dokładnie to, co przewidywało zlecenie:
nagłówek („Korupcja w Narodowym Centrum Nauki — archiwum dowodów sygnalisty" +
Dr Witold Kilarski), streszczenie sprawy **410 słów** (wymagane 400–500), jeden
wyróżniony cytat (e-mail z konta NCN z 1 czerwca 2020 r.), sześć kart-kafli,
skróconą chronologię z **8 datami**, notę o autorze **78 słów** (limit 120)
i stopkę z kontaktem, linkiem do pełnego archiwum, /sprostowania/ i wersjami
językowymi. Na home nie ma ani jednego odtwarzacza audio, ani jednej
transkrypcji, ani jednego dużego podglądu dokumentu.

## 2. Co przeniesiono i gdzie

Treść była **przenoszona, nie przepisywana**: HTML każdej sekcji jest kopiowany
1:1, razem z cytatami, wulgaryzmami, literówkami w transkrypcjach, oznaczeniami
mówców, tabelami, blockquote'ami, odtwarzaczami i notami „🔒 usunięto fragmenty
prywatne". Ani jedno zdanie nie zostało przeredagowane.

| Sekcja na dawnej stronie głównej | Nowy adres |
| --- | --- |
| Wprowadzenie do sprawy (`#case`) | /wprowadzenie/ **(nowa)** |
| Nagranie 1 — 29 maja 2020 (`#interview`) | /nagrania/1/ **(nowa)** |
| Nagranie 2 — 2 czerwca 2020 (`#interview-3-4`) | /nagrania/2/ **(nowa)** |
| Nagranie 3 — 4 czerwca 2020 (`#interview-4`) | /nagrania/3/ **(nowa)** |
| Nagranie 4 — 10 października 2020 (`#rec-4`) | /nagrania/4/ **(nowa)** |
| Nagranie 5 — 20 marca 2021, cz. A i B (`#rec-5a`) | /nagrania/5/ **(nowa)** |
| Nagranie 6 — telefon osoby NN (`#rec-6`) | /nagrania/6/ **(nowa)** |
| Nagranie 7 — 30 września 2021 (`#rec-7`) | /nagrania/7/ **(nowa)** |
| Kluczowe daty / chronologia (`#timeline`) | /chronologia/ **(nowa)** |
| O mnie + CV (`#about`) | /cv/ **(nowa)** |
| WUM po piśmie dyrektora NCN (`#blocki-cyngiel`) | /wum-blocki-cyngiel/ **(nowa)** |
| List otwarty (`#list-otwarty`) | /list-otwarty/ **(nowa)** |
| Pomoc Ukraińcom (`#ukraina`) | /pomoc-ukraincom/ **(nowa)** |
| Kulturowe analogie (`#kulturowe-analogie`) | /kulturowe-analogie/ **(nowa)** |
| Dyskusja / komentarze (`#comments`) | /dyskusja/ **(nowa)** |
| Drugi rząd zakładek — 121 odnośników do dokumentów | /skorowidz/ **(nowa)**, także /en/, /fr/, /de/, /uk/ |
| Odmowa prokuratury (`#prokuratura-ochonska`) | /prokuratura/ (istniała) |
| Sprawy sądowe (`#courts`) | /sprawy-sadowe/ (istniała) |
| Dokumenty (`#documents`) | /dokumenty/ (istniała) |
| Bezczynność UJ (`#uj-inaction`) | /bezczynnosc-uj/ (istniała) |
| Błocki, Babik, Liana (`#sprawa-blocki-babik-liana`) | /blocki-babik-liana/ (istniała) |
| Maszynowe recenzje / Mudelsee (`#mudelsee`) | /maszynowe-recenzje-ncn/ (istniała) |
| Wniosek o kontrolę (`#wniosek-kontrola-ncn`) | /wniosek-o-kontrole-ncn/ (istniała) |
| Wyrok kafkowski (`#wyrok-kafkowski`) | /wyrok-kafkowski/ (istniała) |
| Sprawa komornika (`#komornik`) | /sprawa-komornika/ (istniała) |
| Sprostowania (`#sprostowania`) | /sprostowania/ (istniała) |

**Treść utracona: 0 akapitów.** Każdy akapit, cytat i plik z dawnej strony
głównej ma dziś odpowiednik na podstronie. Build przerywa pracę, jeśli
jakikolwiek odnośnik albo kotwica nie ma żywego celu — bez tego nie powstałby
żaden plik.

## 3. Nowe podstrony i zachowanie dawnych odnośników

Utworzono **26 nowych adresów**:

- 4 strony-huby działów: /nagrania/, /postepowania/, /instytucje/, /o-mnie/
- 7 podstron nagrań: /nagrania/1/ … /nagrania/7/
- 10 podstron z przeniesioną treścią: /wprowadzenie/, /chronologia/, /cv/,
  /wum-blocki-cyngiel/, /list-otwarty/, /pomoc-ukraincom/, /kulturowe-analogie/,
  /dyskusja/ oraz /skorowidz/ (PL) i skorowidze językowe
- 4 skorowidze językowe: /en/skorowidz/, /fr/skorowidz/, /de/skorowidz/, /uk/skorowidz/

Razem witryna ma teraz 39 adresów w `sitemap.xml` (wcześniej 15).

**Dawne odnośniki — uczciwie o „301":** GitHub Pages nie potrafi wystawić
przekierowania 301 (nie ma serwera, który mógłby je wysłać), a fragment adresu
(`#rec-6`) w ogóle nigdy nie dociera do serwera — obsługuje go wyłącznie
przeglądarka. Dlatego dawne kotwice strony głównej przekierowuję po stronie
przeglądarki: na stronie głównej działa mapa **35 kotwic**, która natychmiast
(`location.replace`, bez wpisu w historii — tak jak przy 301) przenosi na nowy
adres. Przykłady: `/#rec-6` → /nagrania/6/, `/#timeline` → /chronologia/,
`/#case` → /wprowadzenie/, `/#about` → /cv/. Dodatkowo wszystkie odnośniki
wewnątrz witryny zostały przepisane na nowe adresy, a `/404.html` wymienia
wszystkie działy i podstrony. Żaden stary link nie prowadzi w pustkę, ale
**formalnie nie jest to kod 301** i nie mogę tego obiecać w takim brzmieniu.

## 4. Diagnoza Nagrania 6 (martwy odtwarzacz)

Plik: `docs/9.-Lara-tel-do-mnie-Jareniowki_AUD-20231216-WA0001.m4a`

Ustalenia:

1. Ścieżka w kodzie jest **poprawna** — nie ma tu literówki.
2. Rozmiar pliku to **9 467 642 B (9,0 MB)** — daleko poniżej limitu GitHuba
   (100 MB), więc limit nie ma z tym nic wspólnego. Inne nagrania w repozytorium
   mają 15–46 MB i działają.
3. Pliku **nie ma dziś w repozytorium**, ale jest w historii Git (obiekt
   `a1d3b20`). Został usunięty **8 maja 2026 r.** w commicie `71e3a2d`
   „Pilna anonimizacja: usunięcie wrażliwych ekspozycji i danych osobowych".
   W tym samym commicie usunięto też starszą wersję `9-Larua-tel-do-mnie-Jareniowki-AU.mp3`.

**Wniosek: to nie jest awaria, to skutek Twojej własnej decyzji o anonimizacji.**
Dlatego **nie przywróciłem pliku** — to wymaga Twojej decyzji (punkt 5).
Komunikat „plik audio chwilowo niedostępny" zostaje, a na podstronie
/nagrania/6/ w metryczce widnieje „Czas trwania: nieustalony — plik audio
niedostępny".

## 5. LISTA WSZYSTKIEGO, CZEGO NIE RUSZYŁEM, BO WYMAGA TWOJEJ DECYZJI

1. **Plik audio Nagrania 6.** Jest w historii Git i da się go przywrócić jednym
   poleceniem, ale usunąłeś go w commicie o anonimizacji. Decyzje do podjęcia:
   (a) przywrócić w całości, (b) przywrócić wersję ze wyciszonymi fragmentami
   prywatnymi, (c) zostawić komunikat i dopisać przy nim powód
   („usunięto w ramach anonimizacji 8 maja 2026 r."). Nie zrobiłem nic z tych
   trzech rzeczy.
2. **Nagrania 4 i 6 z numeracji dokumentu** (`4.-5-czerwca-2020-rozmowa-Laura-Blocki.MP3`
   i `6.-zal-4-2009281937-...-broni-Mandelsiego-28Sierpnia...MP3`) leżą w `docs/`,
   ale nie mają na witrynie ani opisu, ani podstrony. Nie utworzyłem ich —
   nie znam Twojego opisu znaczenia dowodowego tych rozmów. Odnotowałem to
   w nocie o numeracji.
3. **Treść dawnego drugiego rzędu zakładek** przeniosłem 1:1 do /skorowidz/,
   ale nie oceniałem, czy wszystkie 121 odnośników nadal chcesz publikować
   i w tej kolejności.
4. **Wersje /en/, /fr/, /de/, /uk/ nadal są jednostronicowe** — mają pełną treść
   na jednej stronie i tego nie tknąłem, bo odtłuszczenie ich wymagałoby
   przetłumaczenia streszczenia, opisów kafli i tytułów 26 podstron. Zmieniłem
   w nich wyłącznie nawigację (te same sześć zakładek) i usunąłem drugi rząd
   zakładek. Jeśli chcesz pełną symetrię, potrzebuję tłumaczeń albo zgody na
   ich wygenerowanie.
5. **Etykiety menu w /de/, /fr/, /uk/ są angielskie** (Case, Recordings,
   Documents, Proceedings, Institutions, About me) — zgodnie ze zleceniem przy
   braku tłumaczeń. Czekam na polskie/niemieckie/francuskie/ukraińskie
   odpowiedniki, jeśli mają być przetłumaczone.
6. **Wyśrodkowany tekst na podstronach.** Twój projekt centruje akapity także
   w długich transkrypcjach; to utrudnia czytanie. Na nowej stronie głównej
   i na nowych stronach-hubach ustawiłem tekst do lewej, ale **nie zmieniałem
   wyglądu istniejących podstron** — to Twoja decyzja projektowa.
7. **Arkusz stylów (88 KB) i skrypty (17 KB) nadal są wklejone w każdą stronę.**
   Wyniesienie ich do `/assets/site.css` i `/assets/site.js` zmniejszyłoby każdą
   stronę o ok. 100 KB i przyspieszyło witrynę, ale to zmiana architektury
   — nie robiłem tego bez Twojej zgody.
8. **Wewnątrzstronowe rzędy odnośników** („Przejdź do:", „Nawigacja") usunąłem
   ze strony głównej i z podstron PL, bo zawierały zabronione w menu etykiety
   („Blocki cyngiel", „NCN: maszynowe recenzje") i dublowały nową nawigację.
   Na stronach językowych je **zostawiłem**, bo to jedna długa strona i bez nich
   nie ma jak po niej skakać. Jeśli wolisz inaczej — powiedz.
9. **Nie dotknąłem** żadnego nazwiska, daty, sygnatury, kwoty ani opisu znaczenia
   dowodowego. Nie zmieniłem też numeracji nagrań — ani na stronie, ani
   w dokumencie.
10. **Licznik odwiedzin, film w nagłówku i strona `animation-en.html`** zostały
    bez zmian.

## 6. Wykryte błędy i niespójności + propozycje do /sprostowania/

**A. Zepsuty JavaScript na całej witrynie — błąd istniał już na `main`.**
Główny skrypt witryny (7,2 KB: menu mobilne, płynne przewijanie, zachowanie
nagłówka przy przewijaniu, przycisk „do góry", przeglądarka CV) **nie wykonywał
się w ogóle**, bo generator wstawiał nawias klamrowy w środek wywołania funkcji
i psuł składnię pliku. Sprawdziłem: dokładnie ten sam błąd jest w pliku
`index.html` na gałęzi `main`. Naprawiłem wzorzec w `tools/build.py` i dodałem
kontrolę, która przerywa build, jeśli którykolwiek skrypt inline nie jest
poprawnym JavaScriptem. To poprawka techniczna, nie merytoryczna — nie dotyczy
treści dowodowej.

**B. Numeracja nagrań (1–7 na stronie, 1–10 w dokumencie).** Żadnej numeracji
nie zmieniłem. Do /sprostowania/ dodałem wpis z datą **20 sierpnia 2026 r.**
(kotwica `#errata-numeracja-nagran`) z tabelą przeliczenia, a każda podstrona
nagrania ma jedno zdanie z linkiem do tej noty. Treść wpisu — do Twojego
zatwierdzenia lub przeredagowania:

> **20 sierpnia 2026 — numeracja nagrań na stronie a numeracja w dokumencie
> „analiza_nagran_audio_kompletna"**
> Witryna numeruje nagrania od 1 do 7. Dokument numeruje pliki audio od 1 do 10.
> Żadnej z tych numeracji nie zmieniam — obie funkcjonują w obiegu i obie są
> cytowane w pismach. Tabela przeliczenia: 1→1, 2→2, 3→3, 4→5,
> 5 (części A i B)→7 i 8, 6→9, 7→10. Nagrania 4 (5 czerwca 2020)
> i 6 (28 sierpnia 2020) z numeracji dokumentu nie mają na witrynie własnych
> podstron — pliki audio są w archiwum, ale nie zostały jeszcze opisane.
> Odnotowuję to jako brak, nie jako sprostowanie treści.

**C. Wewnętrzna niespójność liczby nagrań.** Strona pisze o „7 nagraniach", ale
Nagranie 5 to dwa pliki (części A i B), a dawny rząd zakładek wymieniał je
osobno jako „Nagranie 5a" i „Nagranie 5b" — czyli osiem pozycji. Nie zmieniałem
żadnego z tych sformułowań. **Propozycja wpisu do /sprostowania/ (nie wprowadzona):**
jedno zdanie wyjaśniające, że „siedem nagrań" oznacza siedem rozmów, z których
jedna jest zapisana w dwóch plikach.

**D. Data Nagrania 6.** Nazwa pliku źródłowego wskazuje 16 grudnia 2023 r.
(`AUD-20231216`), a nagranie jest opisane w ciągu rozmów z lat 2020–2021.
W metryczce podstrony napisałem wprost „16 grudnia 2023 r. (data pliku
źródłowego)", żeby niczego nie sugerować. **Do Twojego rozstrzygnięcia:** czy
data rozmowy jest tożsama z datą pliku. Nie wpisałem tego do /sprostowania/,
bo nie wiem, która data jest prawdziwa.

**E. Sprostowanie z 1 sierpnia 2026 r. o opisie Nagrania 6** mówi, że to osoba
NN dzwoniła z Krakowa do Jareniówki, ale sam tytuł sekcji nadal brzmi „telefon
NN do mnie, gdy byłem w Jareniówce" — co jest zgodne ze sprostowaniem. Zostawiłem
bez zmian; odnotowuję tylko, że opis nad odtwarzaczem („NN dzwoni do dr.
Kilarskiego z Jareniówki") mówi coś innego niż sprostowanie. **To jest realna
rozbieżność treści — nie poprawiłem jej samowolnie.** Wymaga jednego Twojego
zdania.

## 7. Nowa nawigacja

Dokładnie **sześć zakładek**, w jednym rzędzie, w kolejności i brzmieniu ze
zlecenia: **Sprawa · Nagrania · Dokumenty · Postępowania · Instytucje · O mnie**.

- Każda zakładka jest zwykłym linkiem do strony-huba działu:
  `/` · `/nagrania/` · `/dokumenty/` · `/postepowania/` · `/instytucje/` · `/o-mnie/`.
- **Nie ma rozwijanych menu.** Zgodnie z punktem „prostota jest ważniejsza niż
  efekt wizualny" wybrałem wariant prostszy: sześć linków do hubów, a podnawigacja
  działu to pionowa lista wewnątrz strony huba. Dzięki temu nie ma żadnej
  zależności od hoveru, nie ma pułapek WCAG 1.4.13 i nie ma czego zamykać
  Escapem poza menu mobilnym.
- **Nie ma drugiego rzędu zakładek** — dawny rząd z 15 zakładkami i rozwijanymi
  listami zniknął z całej witryny; jego zawartość jest w /skorowidz/.
- Menu jest przyklejone do góry (sticky), w jednym rzędzie, bez przewijania
  w poziomie przy 375, 768 i 1440 px.
- Poniżej 900 px: klasyczne menu rozwijane przyciskiem (hamburger), pionowa
  lista, zero zależności od hoveru. Otwiera się Enterem i Spacją, zamyka
  Escapem (fokus wraca na przycisk), zamyka się też po kliknięciu linku.
- Przypisanie treści do działów: Sprawa → strona główna + /wprowadzenie/
  + /chronologia/; Nagrania → hub + 7 podstron; Dokumenty → /dokumenty/
  (+ /skorowidz/); Postępowania → prokuratura, sprawy sądowe, wyrok kafkowski,
  komornik, wniosek o kontrolę; Instytucje → Mudelsee/NCN, bezczynność UJ, WUM,
  Błocki–Babik–Liana; O mnie → CV, sprostowania, list otwarty, pomoc Ukraińcom,
  kulturowe analogie, dyskusja.
- Wersje językowe PL / EN / FR / DE / UA — osobno i dyskretnie, po prawej
  stronie nagłówka, jak dotychczas.
- W menu nie występuje żadna z zabronionych etykiet („Blocki cyngiel",
  „NCN: maszynowe recenzje", nazwy pojedynczych nagrań i pism) — pozostały
  wyłącznie jako tytuły artykułów. Kontrola w `tools/verify.py` tego pilnuje.

## 8. Testy

| Test | Wynik |
| --- | --- |
| Build (`python3 tools/build.py`) | kończy się bez błędów, 41 plików |
| Kontrola własna buildu: zerwane linki i kotwice | 0 — build przerwałby pracę |
| Kontrola składni JavaScriptu (nowa) | wszystkie skrypty poprawne |
| `python3 tools/verify.py` (12 grup kontroli) | **0 błędów** |
| Kody odpowiedzi wszystkich 39 adresów z sitemap + 404, robots, sitemap, animacja, PDF-y, MP3 | **48 × 200**, brak 404 |
| Szerokości 375 / 768 / 1440 px | brak przewijania w poziomie (scrollWidth = innerWidth) |
| Menu klawiaturą (1440 px) | Tab przechodzi: skip-link → logo → 6 zakładek → PL/EN/FR/DE/UA |
| Menu mobilne (375 px) | Enter otwiera, Spacja otwiera, Escape zamyka i przywraca fokus |
| Nagrania i dokumenty otwierają się | tak; odtwarzacze bez `autoplay` |
| Nagranie 6 | komunikat o niedostępnym pliku (plik usunięty w maju 2026 r.) |

Jedyny adres zwracający 404 to sam plik audio Nagrania 6 — sprawdzany celowo,
bezpośrednio; **na witrynie nie ma do niego żadnego odnośnika**.

Raport techniczny weryfikacji: `raport/verify-2026-08-20.txt`.
Pomiary: `raport/pomiar-przed.json`, `raport/pomiar-po.json`, powtarzalny pomiar:
`python3 tools/measure_home.py`.

## 9. Gałąź, commity, podgląd

**Gałąź:** `odtluszczenie-2026-08` (baza: `40dc877`). `main` nie był modyfikowany
ani razu — żadnego commita, żadnego pusha na `main`.

Commity (logiczne, w kolejności):

1. `b403fa9` — Zadanie 0: kopia stanu początkowego, inwentaryzacja, skrypt cofania zmian
2. `d207952` — Zadanie 1+4: nowa treść strony głównej i nota o numeracji (źródło `src/`)
3. `641e84b` — Zadania 1–5: generator — wydzielenie podstron, sześć zakładek, dostępność, SEO
4. `3d52723` — Zadania 1–5: przebudowa wygenerowanych stron
5. `e3bef86` — Zadanie 6: testy, naprawa składni JS witryny, raport końcowy
6. `9d88f79` — Zadanie 6: zapis kodów odpowiedzi 46 adresów (46 × 200, zero 404)
7. `c778ff9` — raport: uzupełnienie listy commitów i adresu gałęzi
8. `68ca1ad` — Nagranie 6 + szybkość: poprawka opisu rozmowy i przyspieszenie witryny
9. `86527f8` — raport: aneks o Nagraniu 6 i przyspieszeniu witryny
10. (ten commit) — obcięcie fontów do używanych znaków i minifikacja arkusza stylów

Gałąź jest wypchnięta na GitHub:
https://github.com/LudvigBoltzmann/KorupcjaNCN/tree/odtluszczenie-2026-08

Podgląd: GitHub Pages buduje wyłącznie z `main` (workflow `build-pages` ma
warunek `github.ref == refs/heads/main`), więc gałąź robocza nie ma własnego
adresu w internecie. Podgląd zrobiłem jako osobną, prywatną kopię witryny —
link przekazuję w wiadomości. Aby zobaczyć gałąź lokalnie:

```bash
git fetch origin odtluszczenie-2026-08
git checkout odtluszczenie-2026-08
python3 -m http.server 8000    # potem otwórz http://localhost:8000/
```

Cofnięcie wszystkiego jednym poleceniem: `bash raport/przywroc-stan-przed.sh`.

## 10. Czy zmiany są gotowe do scalenia z `main`?

**Tak, technicznie są gotowe — ale nie scalam i czekam na Twoje „scalamy".**

Wszystkie kryteria odbioru są spełnione: objętość home spadła o 88,3% (wymóg
≥ 80%), zero akapitów bez odpowiednika na podstronie, 100% adresów odpowiada
kodem 200, menu ma dokładnie sześć klikalnych zakładek, całe menu przechodzi
Tabem i zamyka się Escapem, na mobile nie ma zależności od hoveru ani przewijania
w poziomie, gałąź `main` jest nietknięta.

Zanim scalisz, przeczytaj punkt 5 (dziesięć rzeczy czekających na Twoją decyzję)
i punkt 6 — w szczególności **rozbieżność E** (opis Nagrania 6 nad odtwarzaczem
kontra sprostowanie z 1 sierpnia 2026 r.) oraz brzmienie noty o numeracji, którą
dodałem do /sprostowania/. To jedyne miejsca, w których dotknąłem czegoś
bliskiego treści — i jedyne, które wymagają Twojego podpisu.

Po scaleniu na `main` workflow `build-pages` przebuduje strony automatycznie
(źródło i generator są w commitach), więc nie trzeba nic uruchamiać ręcznie.

## 11. Aneks z 20 sierpnia 2026 r. (wieczór): szybkość i Nagranie 6

Na Twoje polecenie: „Nagranie 6 po prostu opuść… ważniejsze, by strona działała
jak najszybciej… popraw, że dzwoniła ona do mnie".

### 11a. Nagranie 6 — zrobione

- **Opis poprawiony we wszystkich pięciu wersjach językowych:** to osoba NN
  zadzwoniła do Ciebie — ze swojego telefonu komórkowego z Krakowa na Twoją
  komórkę, gdy przebywałeś w Jareniówce; stąd zakłócenia w nagraniu. Wcześniejsze
  zdanie („NN dzwoni do dr. Kilarskiego z Jareniówki") było odwrotnością faktu.
- **Dwa nowe wpisy w /sprostowania/ z datą 20 sierpnia 2026 r.** — bez cichej
  korekty: jeden o kierunku rozmowy (`#errata-nagranie-6-kierunek-rozmowy`),
  drugi o tym, że plik audio nie jest publikowany i może być duplikatem innej
  rozmowy (`#errata-nagranie-6-plik`).
- **Komunikat przy odtwarzaczu nie obiecuje już terminu.** Brzmi: „Plik audio
  tego nagrania nie jest publikowany — nie mam pewności, czy nie jest duplikatem
  innej z opublikowanych rozmów. Opis tematyczny i numeracja pozostają bez zmian"
  plus link do noty. Metryczka podstrony: data „nieustalona (plik audio
  niepublikowany)".
- **Numeracji nie zmieniono.** Nagranie zostaje jako 6 na stronie i 9 w dokumencie
  analizy; tabela przeliczenia bez zmian. Gdy ustalisz, co zawierało, wystarczy
  wgrać plik i usunąć jedno zdanie z noty.

### 11b. Szybkość — co zrobiłem

| Zmiana | Efekt |
| --- | --- |
| Wspólny arkusz stylów (93 KB) wyniesiony do `assets/site-*.css` | przeglądarka pobiera go **raz dla całej witryny**, potem z pamięci |
| Skrypty (6 KB) wyniesione do `assets/site-*.js` z `defer` | nie blokują renderowania, też z cache |
| Fonty Inter i Source Serif 4 hostowane lokalnie (`assets/fonts/`) | **zero zapytań do fonts.googleapis.com i fonts.gstatic.com**, brak blokującego arkusza z obcego serwera, `font-display: swap`; pliki zmienne odduplikowane (28 reguł → 12 plików) |
| Osadzone odtwarzacze YouTube → zasłona z przyciskiem | na home 1, na stronie kulturowych analogii 9, na wersjach językowych 10 — **przed kliknięciem strona nie kontaktuje się z YouTube w ogóle**; oszczędność ok. 600 KB i kilkunastu zapytań na film; miniatura filmu dokumentalnego jest lokalna (58 KB) |
| Wszystkie obrazy: `loading="lazy"`, `decoding="async"` | przeglądarka nie ściąga tego, czego nie widać |

Waga plików HTML (to, co przeglądarka pobiera przy każdym wejściu):

| Strona | Przed | Po |
| --- | --- | --- |
| Strona główna | 249,8 KB | **46,8 KB** (−81%) |
| /nagrania/6/ | — | 31,3 KB |
| /sprostowania/ | 145,7 KB | 29,8 KB |
| /kulturowe-analogie/ | — | 33,7 KB |
| /en/ | 342,5 KB | 227,4 KB |

Pierwsze wejście na stronę główną: 46,8 KB HTML + 93 KB CSS + 6 KB JS + fonty
(pobierane tylko te potrzebne do polskich znaków) + 104 KB obrazów.
**Każde następne wejście na dowolną podstronę to już tylko ok. 30–47 KB** — styl,
skrypty i fonty są w pamięci przeglądarki. Wcześniej każda strona ciągnęła
150–250 KB od nowa, plus arkusz z Google i pełny odtwarzacz YouTube.

Serwer GitHub Pages wysyła te pliki skompresowane (gzip), więc realny transfer
jest jeszcze około pięciokrotnie mniejszy.

### 11c. Czytelność

Akapity i listy w treści są teraz wyrównane do lewej (nagłówki zostały
wyśrodkowane jak dotąd). To była propozycja z punktu 5.6 — długie transkrypcje
wyśrodkowane męczą oko. Cofnięcie to usunięcie jednego bloku w `EXTRA_CSS`.

### 11d. Czego nadal nie ruszyłem

1. **Pliku Nagrania 6 nie przywróciłem** — zgodnie z Twoją decyzją zostaje
   nieopublikowany. Jest w historii Git (obiekt `a1d3b20`), więc nic nie przepadło.
2. **Nagrania 4 i 6 z numeracji dokumentu** wciąż bez podstron (brak Twojego opisu).
3. **Wersje /en/, /fr/, /de/, /uk/ nadal jednostronicowe**; etykiety menu w /de/,
   /fr/, /uk/ pozostają angielskie.
4. **Dalsze przyspieszenie jest możliwe**, ale wymaga Twojej zgody: obcięcie fontów
   tylko do znaków faktycznie używanych (z ok. 350 KB do ok. 40 KB), rezygnacja
   z jednej z trzech grubości Inter, oraz minifikacja arkusza stylów. Nie robiłem
   tego, bo każda z tych rzeczy może subtelnie zmienić wygląd.
5. **Rozbieżność E z punktu 6 jest już usunięta** — to była właśnie ta sprawa
   z kierunkiem rozmowy w Nagraniu 6.

Testy po tych zmianach: build bez błędów, `tools/verify.py` — 0 błędów (12 grup
kontroli), 46 adresów × 200, brak przewijania w poziomie przy 375/768/1440 px,
menu mobilne otwierane Enterem i Spacją oraz zamykane Escapem, klik na zasłonę
filmu uruchamia odtwarzacz z autoodtwarzaniem.

## 12. Aneks drugi (20 sierpnia 2026 r., popołudnie): obcięte fonty i zminifikowany arkusz stylów

Na Twoje polecenie: „Obetnij jeszcze fonty i zminifikuj arkusz stylów".

### 12a. Fonty — obcięte

`tools/pobierz_fonty.py` robi teraz trzy rzeczy zamiast jednej:

1. pobiera z Google te same pliki co dotąd (krój pisma bez zmian: Inter
   i Source Serif 4, licencja OFL),
2. **zawęża osie fontów zmiennych**: pliki Google zawierają całą rodzinę grubości
   100–900 oraz osobną oś rozmiaru optycznego 8–60 pt, a witryna używa grubości
   400/500/600 (Inter) i 400/600/700 (Source Serif). Oś rozmiaru optycznego jest
   przypięta do wartości domyślnej 20, zakres grubości zawężony,
3. **obcina każdy plik do znaków, które faktycznie występują na witrynie** plus
   stały zapas (podstawowa łacina, polskie, francuskie i niemieckie znaki
   diakrytyczne, typografia — pauzy, cudzysłowy „ ", …, strzałki — oraz cyrylica
   ukraińska dla wersji /uk/). Razem 503 znaki; sprawdzane jest, czy dany znak
   naprawdę jest w foncie.

| Fonty | Przed | Po |
| --- | --- | --- |
| Wszystkie pliki w repozytorium | 671,5 KB (12 plików) | **136,4 KB (9 plików)** — −80% |
| Co ściąga polski czytelnik (maksymalnie) | ok. 440 KB | **98,5 KB** |
| Zapytania do fonts.googleapis.com / gstatic | 2 połączenia + arkusz blokujący | **0** |

Sprawdzone w przeglądarce: polskie znaki (ą ć ę ł ń ó ś ź ż) i ukraińska
cyrylica renderują się właściwym krojem, `document.fonts.status = "loaded"`,
21 reguł @font-face.

### 12b. Arkusz stylów — zminifikowany

Minifikacja jest **zachowawcza i sprawdzana przez build**: usuwane są komentarze
i zbędne białe znaki, ale nic wewnątrz cudzysłowów ani wewnątrz nawiasów
(`calc()`, `@media (min-width: 768px)`, `rgba()`) nie jest ruszane — tam spacje
mają znaczenie. Po minifikacji build porównuje liczbę bloków i deklaracji
z wersją źródłową; przy jakiejkolwiek różnicy przerywa pracę i nic nie zapisuje.

| Arkusz stylów | Przed | Po |
| --- | --- | --- |
| `assets/site-*.css` | 93,4 KB | **67,9 KB** (−27%) |

Wszystkie 28 zapytań `@media` i 4 wyrażenia `calc()` przeszły bez zmian.
Sprawdzone w przeglądarce: identyczny wygląd (te same kroje, rozmiary, obramowania
kafli 1 px / promień 8 px, tło cytatu, sticky nagłówek, dwie kolumny kafli
przy 1280 px, jedna przy 375 px).

### 12c. Bilans wagi po wszystkich zmianach

Pierwsze wejście na stronę główną (bez obrazów): **225,6 KB** — 46,8 KB HTML
+ 67,9 KB CSS + 6,1 KB JS + 6,3 KB deklaracji fontów + maks. 98,5 KB samych
fontów. Każda następna podstrona to **30–47 KB**, bo styl, skrypty i fonty
są już w pamięci przeglądarki. Serwer wysyła to skompresowane (gzip), więc
realny transfer jest jeszcze kilkukrotnie mniejszy.

Dla porównania stan na `main`: 249,8 KB samego HTML strony głównej za każdym
wejściem, plus arkusz z Google Fonts (dwa dodatkowe połączenia, ok. 440 KB
fontów), plus pełny odtwarzacz YouTube ładowany od razu (ok. 600 KB).

### 12d. Co można cofnąć jednym ruchem

- Minifikacja: usunięcie wywołania `minify_css` w `externalize_assets`.
- Obcięcie fontów: `AXIS_LIMITS = {}` w `tools/pobierz_fonty.py` i ponowne
  uruchomienie skryptu (wróci pełny zakres grubości i rozmiarów optycznych).
- Cały pakiet: `bash raport/przywroc-stan-przed.sh`.

Testy po tych zmianach: build bez błędów (z kontrolą struktury CSS
i składni JS), `tools/verify.py` — 0 błędów, 46 adresów × 200, brak przewijania
w poziomie przy 375/768/1440 px, menu mobilne działa Enterem, Spacją i Escapem.
