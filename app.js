/* app.js — Routing, Language Switching, Theme Toggle
   For Dr. Witold Kilarski Whistleblower Website
*/

(function () {
  'use strict';

  // ============================================
  // TRANSLATIONS
  // ============================================
  const translations = {
    // Header
    'header-subtitle': { pl: 'Sygnalista / Whistleblower', en: 'Whistleblower' },
    'nav-home': { pl: 'Strona główna', en: 'Home' },
    'nav-corruption': { pl: 'Korupcja NCN', en: 'NCN Corruption' },
    'nav-cases': { pl: 'Sprawy', en: 'Cases' },
    'nav-timeline': { pl: 'Chronologia', en: 'Timeline' },

    // Home
    'home-title': { pl: 'Dr Witold Kilarski — Sygnalista', en: 'Dr. Witold Kilarski — Whistleblower' },
    'home-subtitle': { pl: 'Ujawnianie korupcji w polskiej nauce', en: 'Exposing corruption in Polish science' },
    'home-p1': {
      pl: 'Jestem naukowcem z międzynarodowym dorobkiem (PhD Uppsala, postdoc EPFL/Bordeaux/University of Chicago), specjalizującym się w biologii. Mój indeks Hirsha wynosi 20, mam 42 publikacje, w tym w Nature i Science.',
      en: 'I am a scientist with an international track record (PhD Uppsala, postdoc EPFL/Bordeaux/University of Chicago), specializing in biology. My H-index is 20, with 42 publications including in Nature and Science.'
    },
    'home-p2': {
      pl: 'Po powrocie do Polski w 2020 roku, ujawniłem systemową korupcję w Narodowym Centrum Nauki (NCN) — najważniejszej instytucji finansującej badania naukowe w Polsce. W odpowiedzi spotkałem się z represjami: odrzuceniem grantów, procesami sądowymi i zniszczeniem kariery naukowej.',
      en: 'After returning to Poland in 2020, I exposed systemic corruption at the National Science Centre (NCN) — Poland\'s most important institution funding scientific research. In response, I faced retaliation: grant rejections, lawsuits, and the destruction of my scientific career.'
    },
    'home-p3': {
      pl: 'Ta strona przedstawia dokumentację moich spraw jako sygnalisty — dowody korupcji w NCN, przebieg postępowań sądowych oraz działania prawne, które podjąłem w obronie prawdy i interesu publicznego.',
      en: 'This website presents the documentation of my whistleblower cases — evidence of corruption at NCN, the course of court proceedings, and the legal actions I have taken in defense of truth and the public interest.'
    },
    'contact-phone': { pl: 'Telefon', en: 'Phone' },
    'contact-address': { pl: 'Adres', en: 'Address' },

    // Key Persons
    'persons-title': { pl: 'Osoby wymienione w sprawie', en: 'Persons named in the case' },
    'person-blocki': { pl: 'Były dyrektor NCN, główny sprawca szantażu', en: 'Former NCN Director, main perpetrator of blackmail' },
    'person-liana': { pl: 'Wicedyrektor NCN', en: 'NCN Vice-Director' },
    'person-laura': { pl: 'Kierownik Wydziału Kontroli NCN, przekazała ultimatum, później pozwała mnie', en: 'Head of NCN Audit Department, delivered the ultimatum, later sued me' },
    'person-drag': { pl: 'Politechnika Wrocławska, żądał wycofania grantu', en: 'Wrocław University of Technology, demanded grant withdrawal' },
    'person-mudelsee': { pl: 'Ekspert recenzent, fałszował recenzje (copy-paste)', en: 'Expert reviewer, falsified reviews (copy-paste)' },
    'person-zieba': { pl: 'Mój były adwokat (Kancelaria „Lux Legis"), 14 zarzutów dyscyplinarnych', en: 'My former lawyer ("Lux Legis" firm), 14 disciplinary charges' },
    'person-klis': { pl: 'Pełnomocnik NCN, złożył apelację żądając skazania', en: 'NCN\'s counsel, filed appeal demanding conviction' },
    'person-henrych': { pl: 'Sędzia sprawy karnej, darowizna 400 000 PLN w 2023', en: 'Criminal case judge, 400,000 PLN donation in 2023' },
    'person-pers': { pl: 'Asesor sądowy, nałożył grzywnę 5000 PLN', en: 'Court Assessor, imposed 5,000 PLN fine' },

    // Corruption page
    'corruption-title': { pl: 'Korupcja w Narodowym Centrum Nauki (NCN)', en: 'Corruption at the National Science Centre (NCN)' },
    'corruption-h2-blackmail': { pl: 'Szantaż (art. 230 KK)', en: 'Blackmail (Art. 230 Polish Criminal Code)' },
    'corruption-blackmail-p1': {
      pl: '29 maja 2020 roku Laura Bandura-Morgan, kierownik Wydziału Kontroli NCN, przekazała mi ultimatum od dyrektora NCN Zbigniewa Błockiego: muszę wycofać swój grant z NAWA (Narodowa Agencja Wymiany Akademickiej, program „Polskie Powroty"), bo inaczej ona straci pracę w NCN. Żądanie to zostało wystosowane na polecenie prof. Marcina Drąga z Politechniki Wrocławskiej — bez jakiejkolwiek podstawy prawnej, ponieważ NAWA jest instytucją całkowicie niezależną od NCN (powołaną odrębną ustawą z 7 lipca 2017 r., z siedzibą w Warszawie, podczas gdy NCN ma siedzibę w Krakowie).',
      en: 'On May 29, 2020, Laura Bandura-Morgan, Head of the Audit Department at NCN, delivered an ultimatum from NCN Director Zbigniew Błocki: I must withdraw my grant application from NAWA (National Agency for Academic Exchange, "Polish Returns" program), or she would lose her job at NCN. This demand was made at the behest of Prof. Marcin Drąg from the Wrocław University of Technology — without any legal basis, as NAWA is an institution entirely independent of NCN (established by a separate act of July 7, 2017, headquartered in Warsaw, while NCN is based in Kraków).'
    },
    'corruption-blackmail-p2': {
      pl: 'Około 2 godziny po tym zdarzeniu przeprowadziłem 1,5-godzinny wywiad z Laurą, w którym opisała mechanizmy korupcji w NCN. W następnych dniach (2 i 4 czerwca 2020) Laura nagrała trzy rozmowy ze swoim szefem Błockim — moją nagrywarką, którą przypiąłem jej między piersiami przed spotkaniami.',
      en: 'Approximately 2 hours after this event, I conducted a 1.5-hour interview with Laura, in which she described the mechanisms of corruption at NCN. In the following days (June 2 and 4, 2020), Laura recorded three conversations with her boss Błocki — using my recording device, which I attached between her breasts before the meetings.'
    },
    'corruption-h2-access': { pl: 'Nieuprawniony dostęp do danych (art. 267 KK)', en: 'Unauthorized Data Access (Art. 267 Polish Criminal Code)' },
    'corruption-access-p1': {
      pl: 'Z nagrań wynika, że Błocki i wicedyrektor Wajs czytali prywatne wiadomości Laury na Messengerze — w tym rozmowy dotyczące mnie i naszego wyjazdu do Peru.',
      en: 'The recordings reveal that Błocki and Vice-Director Wajs read Laura\'s private Messenger messages — including conversations about me and our trip to Peru.'
    },
    'corruption-h2-falsification': { pl: 'Fałszowanie recenzji grantowych (art. 270 KK)', en: 'Falsification of Grant Reviews (Art. 270 Polish Criminal Code)' },
    'corruption-falsification-p1': {
      pl: 'W maju 2020 roku, w konkursie GRIEG, ekspert Manfred Mudelsee stosował metodę „kopiuj-wklej" przy recenzowaniu wniosków grantowych — co najmniej 10 wniosków (m.in. od Kowalczuka, Zaborskiej, Kuliskiego z IOPAN) otrzymało identyczne fragmenty recenzji, z tymi samymi błędami merytorycznymi (np. błędne dane o stażu badaczy). Laura Bandura-Morgan zgłosiła to naruszenie do komisji etycznej NCN w maju 2020 roku (naruszenie zasad DORA). Mimo to, dyrektor Błocki uniewinnił Mudelsee decyzją z 4 grudnia 2020 roku.',
      en: 'In May 2020, during the GRIEG competition, expert Manfred Mudelsee used a "copy-paste" method when reviewing grant applications — at least 10 applications (including those from Kowalczuk, Zaborska, Kuliski at IOPAN) received identical review fragments, with the same factual errors (e.g., incorrect data about researchers\' tenure). Laura Bandura-Morgan reported this violation to the NCN ethics committee in May 2020 (violation of DORA principles). Despite this, Director Błocki acquitted Mudelsee by decision of December 4, 2020.'
    },
    'corruption-h2-nepotism': { pl: 'Nepotyzm i konflikty interesów (art. 231 KK)', en: 'Nepotism and Conflicts of Interest (Art. 231 Polish Criminal Code)' },
    'corruption-nepotism-intro': {
      pl: 'Analiza przyznawanych grantów ujawnia powiązania między decydentami NCN a beneficjentami:',
      en: 'Analysis of granted awards reveals connections between NCN decision-makers and beneficiaries:'
    },
    'corruption-nepotism-li1': {
      pl: 'Błocki i Liana (wicedyrektor NCN) mieli powiązania z UJ, którego pracownicy otrzymywali nieproporcjonalnie dużo grantów',
      en: 'Błocki and Liana (NCN Vice-Director) had connections to Jagiellonian University, whose employees received a disproportionate number of grants'
    },
    'corruption-nepotism-li2': {
      pl: 'Członek rady NAWA o nazwisku Kaka jednocześnie zasiadał w radzie i uczestniczył w projektach grantowych — naruszenie regulaminu etycznego',
      en: 'A NAWA council member named Kaka simultaneously sat on the council and participated in grant projects — a violation of ethical regulations'
    },
    'corruption-nepotism-li3': {
      pl: 'Prof. Dulak dopisywał granty do swoich publikacji (75 grantów), za co otrzymał jedynie upomnienie po interwencji',
      en: 'Prof. Dulak added grants to his publications (75 grants), for which he received only a reprimand after intervention'
    },
    'corruption-h2-nik': { pl: 'Tuszowanie kontroli NIK (art. 231 KK)', en: 'Cover-up of NIK Audit (Art. 231 Polish Criminal Code)' },
    'corruption-nik-p1': {
      pl: 'W maju 2020 roku Najwyższa Izba Kontroli przeprowadziła kontrolę finansowania badań przez NCN. Wewnętrzne maile NCN (między Błockim, Laurą, Lianą i Wajsem) ujawniają próby ukrycia wyników tej kontroli.',
      en: 'In May 2020, the Supreme Audit Office (NIK) conducted an audit of NCN\'s research funding. Internal NCN emails (between Błocki, Laura, Liana, and Wajs) reveal attempts to conceal the audit results.'
    },
    'corruption-h2-stats': { pl: 'Analiza statystyczna grantów z odwołania', en: 'Statistical Analysis of Appeal Grants' },
    'corruption-stats-intro': {
      pl: 'Dane z lat 2019-2025 ujawniają rażące anomalie:',
      en: 'Data from 2019-2025 reveals glaring anomalies:'
    },
    'stat-label-4grants': { pl: 'Granty z odwołania 2019–2024', en: 'Appeal grants 2019–2024' },
    'stat-label-0grants': { pl: '2020, 2021, 2024', en: '2020, 2021, 2024' },
    'stat-label-46grants': { pl: 'Granty z odwołania 2025', en: 'Appeal grants 2025' },
    'stat-label-26grants': { pl: 'Fundusze Norweskie 2019', en: 'Norwegian Funds 2019' },
    'corruption-stats-li1': {
      pl: 'W latach 2019-2024 NCN przyznał jedynie 4 granty z odwołania',
      en: 'From 2019-2024, NCN granted only 4 grants on appeal'
    },
    'corruption-stats-li2': {
      pl: 'W latach 2020, 2021 i 2024 nie przyznano żadnego grantu z odwołania',
      en: 'In 2020, 2021, and 2024, no grants were awarded on appeal'
    },
    'corruption-stats-li3': {
      pl: 'W roku 2025, nagle przyznano aż 46 grantów z odwołania',
      en: 'In 2025, suddenly 46 grants were awarded on appeal'
    },
    'corruption-stats-li4': {
      pl: 'W 2019 roku, w ramach programu współfinansowanego z Funduszy Norweskich, przyznano aż 26 grantów — anomalia statystyczna niezgodna z rozkładem normalnym',
      en: 'In 2019, under the Norwegian Funds co-financed program, 26 grants were awarded — a statistical anomaly inconsistent with normal distribution'
    },
    'corruption-h2-evidence': { pl: 'Dowody', en: 'Evidence' },
    'corruption-evidence-intro': {
      pl: 'Dysponuję 19 plikami dowodowymi przekazanymi na pendrive do CBA:',
      en: 'I possess 19 evidence files delivered on a USB drive to the CBA (Central Anti-Corruption Bureau):'
    },
    'evidence-1': { pl: 'Nagrania audio (1-3): Rozmowy Laura–Błocki z maja-czerwca 2020', en: 'Audio recordings (1-3): Laura–Błocki conversations from May-June 2020' },
    'evidence-2': { pl: 'Nagranie 5: Laura o mechanizmach korupcji (październik 2020)', en: 'Recording 5: Laura on corruption mechanisms (October 2020)' },
    'evidence-3': { pl: 'Nagrania 7-8: Rozmowy w mieszkaniu z Laurą (marzec 2021)', en: 'Recordings 7-8: Conversations at home with Laura (March 2021)' },
    'evidence-4': { pl: 'Nagranie 10: Rozmowa telefoniczna po odrzuceniu grantów NAWA (wrzesień 2021)', en: 'Recording 10: Phone conversation after NAWA grant rejections (September 2021)' },
    'evidence-5': { pl: 'Chronologia maili (2020-2021)', en: 'Chronology of emails (2020-2021)' },
    'evidence-6': { pl: 'Analiza recenzji Mudelsee (copy-paste)', en: 'Analysis of Mudelsee reviews (copy-paste)' },
    'evidence-7': { pl: 'Dokumenty kontroli NIK', en: 'NIK audit documents' },
    'evidence-8': { pl: 'Wewnętrzna korespondencja NCN', en: 'Internal NCN correspondence' },

    // Cases page
    'cases-title': { pl: 'Postępowania sądowe', en: 'Legal Proceedings' },
    'case-court': { pl: 'Sąd:', en: 'Court:' },
    'case-subject': { pl: 'Przedmiot:', en: 'Subject:' },
    'case1-title': { pl: '1. Sprawa karna: NCN vs. Kilarski (sygn. II K 321/23/P)', en: '1. Criminal Case: NCN vs. Kilarski (Case No. II K 321/23/P)' },
    'case1-court': { pl: 'Sąd Rejonowy dla Krakowa-Podgórza → Sąd Okręgowy w Krakowie (apelacja)', en: 'District Court for Kraków-Podgórze → Regional Court in Kraków (appeal)' },
    'case1-subject': { pl: 'NCN (oskarżyciel prywatny) oskarżyło mnie o zniesławienie (art. 212 k.k.) za opublikowanie autentycznej korespondencji mailowej ujawniającej korupcję.', en: 'NCN (private prosecutor) charged me with defamation (Art. 212 Polish Criminal Code) for publishing authentic email correspondence exposing corruption.' },
    'case1-verdict-label': { pl: 'Wyrok I instancji (4.04.2025):', en: 'First Instance Verdict (April 4, 2025):' },
    'case1-verdict': { pl: 'Warunkowe umorzenie postępowania — sąd uznał, że czyn miał miejsce, ale nie skazał mnie. Zasądzono 2000 zł na Fundusz Pomocy Pokrzywdzonym i koszty 1728 zł.', en: 'Conditional discontinuation — the court found the act occurred but did not convict me. 2,000 PLN to the Victims\' Fund and 1,728 PLN in costs were ordered.' },
    'case1-appeal-label': { pl: 'Apelacja NCN:', en: 'NCN\'s Appeal:' },
    'case1-appeal': { pl: 'Adwokat NCN Maciej Kliś złożył apelację 12.06.2025, domagając się skazania. Twierdzi, że warunkowe umorzenie jest zbyt łagodne.', en: 'NCN lawyer Maciej Kliś filed an appeal on June 12, 2025, demanding a conviction, arguing the conditional discontinuation was too lenient.' },
    'case1-response-label': { pl: 'Moja odpowiedź na apelację:', en: 'My Response to Appeal:' },
    'case1-response': { pl: 'Złożyłem odpowiedź argumentując m.in. ochronę sygnalisty (ustawa z 14.06.2024 r., Dyrektywa EU 2019/1937), prawdziwość zarzutów (art. 213 k.k.), kryteria Guja (ECHR), oraz podniosłem kwestię darowizny sędziego Henrycha w wysokości 400 000 PLN w 2023 roku.', en: 'I filed a response arguing whistleblower protection (Act of June 14, 2024, EU Directive 2019/1937), truthfulness of allegations (Art. 213 Criminal Code), Guja criteria (ECHR), and raised the issue of Judge Henrych\'s 400,000 PLN donation in 2023.' },

    'case2-title': { pl: '2. Sprawa cywilna: Laura Bandura-Morgan vs. Kilarski (sygn. I C 1671/22 → I ACa 3378/25)', en: '2. Civil Case: Laura Bandura-Morgan vs. Kilarski (Case No. I C 1671/22 → I ACa 3378/25)' },
    'case2-court': { pl: 'Sąd Okręgowy w Krakowie → Sąd Apelacyjny w Krakowie', en: 'Regional Court in Kraków → Court of Appeal in Kraków' },
    'case2-subject': { pl: 'Laura Bandura-Morgan pozwała mnie o ochronę dóbr osobistych za opublikowanie prawdy o szantażu w 2021 roku — mimo że to ona bezpośrednio przekazała mi ultimatum Błockiego. Paradoksalnie, nie pozwała ani Błockiego, ani Drąga (którego — jak wynika z nagrań — uważa za „zbyt potężnego").', en: 'Laura Bandura-Morgan sued me for personal rights protection for publishing the truth about the blackmail in 2021 — despite the fact that she herself directly delivered Błocki\'s ultimatum to me. Paradoxically, she did not sue either Błocki or Drąg (whom — as evident from recordings — she considers "too powerful").' },
    'case2-verdict-label': { pl: 'Wyrok I instancji (15.11.2024):', en: 'First Instance Verdict (November 15, 2024):' },
    'case2-verdict': { pl: 'Sąd zasądził ode mnie odszkodowanie (łącznie 38 265,76 zł).', en: 'The court ordered me to pay damages (totaling 38,265.76 PLN).' },
    'case2-appeal-label': { pl: 'Apelacja:', en: 'Appeal:' },
    'case2-appeal': { pl: 'Wnioski dowodowe złożone 8.02.2026. Argumenty: dwóch adwokatów działało na moją niekorzyść, nagrania zablokowane, art. 381 k.p.c.', en: 'Evidence motions filed February 8, 2026. Arguments: two lawyers acted against my interests, recordings blocked, Art. 381 Code of Civil Procedure.' },

    'case3-title': { pl: '3. Zażalenie na grzywnę (postanowienie z 28.01.2026)', en: '3. Complaint Against Fine (Order of January 28, 2026)' },
    'case3-court': { pl: 'Sąd Rejonowy dla Krakowa-Krowodrzy → Sąd Okręgowy', en: 'District Court for Kraków-Krowodrza → Regional Court' },
    'case3-subject': { pl: 'Asesor sądowy Łukasz Pers nałożył na mnie grzywnę 5000 zł z alternatywą aresztu za rzekome naruszenie zakazu publikacji. Sąd sam rozszerzył postępowanie poza zakres wniosku Laury (wykraczając poza swoje kompetencje) i nie zbadał faktu dwukrotnego przejęcia moich kont na Facebooku.', en: 'Court Assessor Łukasz Pers imposed a 5,000 PLN fine with alternative imprisonment for alleged violation of a publication ban. The court itself expanded proceedings beyond the scope of Laura\'s motion (exceeding its competence) and did not examine the fact that my Facebook accounts were twice hijacked.' },
    'case3-args-label': { pl: 'Argumenty zażalenia:', en: 'Complaint Arguments:' },
    'case3-args': { pl: 'Wolność wypowiedzi (art. 54 Konstytucji, art. 10 EKPC), ochrona sygnalisty, niewspółmierność grzywny wobec osoby bezrobotnej, działanie sądu jako de facto pełnomocnika Laury.', en: 'Freedom of expression (Art. 54 Constitution, Art. 10 ECHR), whistleblower protection, disproportionality of fine for an unemployed person, court acting as de facto counsel for Laura.' },

    'case4-title': { pl: '4. Prokuratura (sygn. 4135-1.Ds.96.2022)', en: '4. Prosecution (Case No. 4135-1.Ds.96.2022)' },
    'case4-body': { pl: 'Prokuratura Rejonowa Kraków-Krowodrza wszczęła śledztwo przeciwko Zbigniewowi Błockiemu, ale Prokuratura Rejonowa odmówiła dalszego prowadzenia sprawy. Moje odwołanie zostało odrzucone. Prokurator Ochońska odmówiła wszczęcia śledztwa.', en: 'The District Prosecutor\'s Office in Kraków-Krowodrza initiated an investigation against Zbigniew Błocki, but the Regional Prosecutor\'s Office refused further proceedings. My appeal was rejected. Prosecutor Ochońska refused to open an investigation.' },

    'case5-title': { pl: '5. Skarga dyscyplinarna na adw. Wojciecha Ziębę', en: '5. Disciplinary Complaint Against Lawyer Wojciech Zięba' },
    'case5-filed-label': { pl: 'Złożona do:', en: 'Filed with:' },
    'case5-filed': { pl: 'Okręgowej Rady Adwokackiej w Krakowie (ul. Straszewskiego 17), kopia do NRA', en: 'District Bar Council in Kraków (ul. Straszewskiego 17), copy to Supreme Bar Council' },
    'case5-subject': { pl: '14 zarzutów naruszenia Kodeksu Etyki Adwokackiej (§ 8, 14, 30, 43, 44, 49, 50, 51, 53, 56) oraz 4 artykuły Prawa o adwokaturze.', en: '14 charges of violation of the Code of Legal Ethics (§ 8, 14, 30, 43, 44, 49, 50, 51, 53, 56) and 4 articles of the Law on the Bar.' },
    'case5-charges-label': { pl: '<strong>Kluczowe zarzuty:</strong>', en: '<strong>Key charges:</strong>' },
    'case5-charge1': { pl: 'Kłamstwo CamScanner: Zięba otrzymał decyzję prokuratury 26.07.2024 (data skanu CamScanner), ale twierdził przez 8 tygodni, że „dopiero co ją otrzymał"', en: 'CamScanner lie: Zięba received the prosecutor\'s decision on July 26, 2024 (CamScanner scan date) but claimed for 8 weeks that he had "just received it"' },
    'case5-charge2': { pl: 'Łączne honoraria: 53 000 PLN za sprawy prowadzone z rażącymi zaniedbaniami', en: 'Total fees: 53,000 PLN for cases handled with gross negligence' },
    'case5-charge3': { pl: 'Zablokowanie nagrań — kluczowych dowodów w sprawach', en: 'Blocking of recordings — key evidence in the cases' },
    'case5-charge4': { pl: 'Nieobecność na rozprawach (w tym rozprawie apelacyjnej)', en: 'Absence at hearings (including the appellate hearing)' },
    'case5-charge5': { pl: 'Złożenie tylko jednej kopii apelacji zamiast wymaganych dwóch', en: 'Filing only one copy of the appeal instead of the required two' },
    'case5-charge6': { pl: 'Bezzasadne wypowiedzenie pełnomocnictwa w kluczowym momencie', en: 'Unjustified termination of power of attorney at a critical moment' },

    'case6-title': { pl: '6. Zgłoszenie szkody do ERGO Hestia', en: '6. Insurance Claim Against ERGO Hestia' },
    'case6-policy-label': { pl: 'Polisa OC:', en: 'Liability Policy:' },
    'case6-policy': { pl: 'Certyfikat nr 430002718822, suma gwarancyjna 400 000 EUR', en: 'Certificate No. 430002718822, coverage 400,000 EUR' },
    'case6-claim-label': { pl: 'Roszczenie:', en: 'Claim:' },
    'case6-damage1': { pl: 'Szkoda rzeczywista: 54 493,76 PLN', en: 'Actual damage: 54,493.76 PLN' },
    'case6-damage2': { pl: 'Utracone korzyści (2 lata × 350 000 PLN/rok): 700 000 PLN', en: 'Lost earnings (2 years × 350,000 PLN/year): 700,000 PLN' },
    'case6-damage3': { pl: 'Zadośćuczynienie za krzywdę: 300 000 PLN', en: 'Non-material damages: 300,000 PLN' },
    'case6-basis': { pl: '<strong>Podstawa:</strong> art. 822 § 4 k.c. (actio directa), 9 opisanych nagrań jako dowody', en: '<strong>Legal basis:</strong> Art. 822 § 4 Civil Code (actio directa), 9 described recordings as evidence' },

    'case7-title': { pl: '7. Zawiadomienie do CBA', en: '7. Report to CBA (Central Anti-Corruption Bureau)' },
    'case7-intro': { pl: 'Złożone do Centralnego Biura Antykorupcyjnego z 19 plikami dowodowymi na USB.', en: 'Filed with the Central Anti-Corruption Bureau with 19 evidence files on USB.' },
    'case7-charges-label': { pl: 'Zarzuty:', en: 'Charges:' },
    'case7-charge1': { pl: 'art. 230 KK — szantaż Błockiego', en: 'Art. 230 Criminal Code — Błocki\'s blackmail' },
    'case7-charge2': { pl: 'art. 267 KK — nieuprawniony dostęp do Messengerów', en: 'Art. 267 Criminal Code — unauthorized access to Messenger' },
    'case7-charge3': { pl: 'art. 270 KK — fałszywe recenzje Mudelsee', en: 'Art. 270 Criminal Code — Mudelsee\'s fake reviews' },
    'case7-charge4': { pl: 'art. 231 KK — tuszowanie kontroli NIK', en: 'Art. 231 Criminal Code — cover-up of NIK audit' },
    'case7-named': { pl: '<strong>Osoby wymienione:</strong> Zbigniew Błocki, Marcin Liana, Laura Bandura-Morgan, Marcin Drąg', en: '<strong>Named individuals:</strong> Zbigniew Błocki, Marcin Liana, Laura Bandura-Morgan, Marcin Drąg' },

    // Timeline
    'timeline-title': { pl: 'Chronologia wydarzeń', en: 'Timeline of Events' },
    'tl-1': { pl: 'Praca naukowa w Szwajcarii (EPFL, ~100 000 CHF/rok)', en: 'Scientific work in Switzerland (EPFL, ~100,000 CHF/year)' },
    'tl-2': { pl: 'Research Asst. Prof., University of Chicago (~100 000 USD/rok)', en: 'Research Asst. Prof., University of Chicago (~100,000 USD/year)' },
    'tl-3': { pl: 'Powrót do Polski, złożenie grantów Grieg (NCN) i POWROTY (NAWA)', en: 'Return to Poland, grant applications for Grieg (NCN) and POWROTY (NAWA)' },
    'tl-4-date': { pl: '29.05.2020', en: 'May 29, 2020' },
    'tl-4': { pl: 'Szantaż: Błocki żąda wycofania grantu NAWA przez Laurę B-M', en: 'Blackmail: Błocki demands withdrawal of NAWA grant via Laura B-M' },
    'tl-5-date': { pl: '29.05.2020', en: 'May 29, 2020' },
    'tl-5': { pl: 'Nagranie 1: 1,5h wywiad z Laurą po szantażu', en: 'Recording 1: 1.5h interview with Laura after blackmail' },
    'tl-6-date': { pl: '02-04.06.2020', en: 'June 2-4, 2020' },
    'tl-6': { pl: 'Nagrania 2-3: Laura nagrywa rozmowy z Błockim', en: 'Recordings 2-3: Laura records conversations with Błocki' },
    'tl-7-date': { pl: '05.2020', en: 'May 2020' },
    'tl-7': { pl: 'Mudelsee: copy-paste recenzje w konkursie GRIEG', en: 'Mudelsee: copy-paste reviews in GRIEG competition' },
    'tl-8-date': { pl: '05.2020', en: 'May 2020' },
    'tl-8': { pl: 'Kontrola NIK w NCN', en: 'NIK audit at NCN' },
    'tl-9-date': { pl: '10.2020', en: 'Oct 2020' },
    'tl-9': { pl: 'Nagranie 5: Laura o korupcji w NCN', en: 'Recording 5: Laura on corruption at NCN' },
    'tl-10-date': { pl: '11.2020', en: 'Nov 2020' },
    'tl-10': { pl: 'Maile do Błockiego, Liany — odpowiada tylko Drąg', en: 'Emails to Błocki, Liana — only Drąg responds' },
    'tl-11-date': { pl: '04.12.2020', en: 'Dec 4, 2020' },
    'tl-11': { pl: 'Błocki uniewinnia Mudelsee', en: 'Błocki acquits Mudelsee' },
    'tl-12-date': { pl: '03.2021', en: 'Mar 2021' },
    'tl-12': { pl: 'Nagranie 7: Laura w mieszkaniu (konflikt Kaka, regulamin)', en: 'Recording 7: Laura at apartment (Kaka conflict, regulations)' },
    'tl-13': { pl: 'Publikacja prawdy o szantażu', en: 'Publication of truth about blackmail' },
    'tl-14-date': { pl: '09.2021', en: 'Sep 2021' },
    'tl-14': { pl: 'Nagranie 10: po odrzuceniu grantów NAWA', en: 'Recording 10: after NAWA grant rejections' },
    'tl-15': { pl: 'Zatrudnienie adw. Wojciecha Zięby (32 000 PLN za zawiadomienie)', en: 'Hiring lawyer Wojciech Zięba (32,000 PLN for notification)' },
    'tl-16': { pl: 'Zawiadomienie do prokuratury — odmowa prokurator Ochońskiej', en: 'Report to prosecution — Prosecutor Ochońska refuses' },
    'tl-17': { pl: 'Pozew Laury B-M (I C 1671/22) i akt oskarżenia NCN (II K 321/23/P)', en: 'Laura B-M\'s lawsuit (I C 1671/22) and NCN indictment (II K 321/23/P)' },
    'tl-18-date': { pl: '04.04.2025', en: 'Apr 4, 2025' },
    'tl-18': { pl: 'Wyrok: warunkowe umorzenie w sprawie NCN', en: 'Verdict: conditional discontinuation in NCN case' },
    'tl-19-date': { pl: '15.11.2024', en: 'Nov 15, 2024' },
    'tl-19': { pl: 'Wyrok w sprawie cywilnej Laury — zasądzono 38 265,76 PLN', en: 'Civil case verdict — 38,265.76 PLN ordered' },
    'tl-20-date': { pl: '16.01.2025', en: 'Jan 16, 2025' },
    'tl-20': { pl: 'Zięba składa apelację — tylko 1 kopię zamiast 2', en: 'Zięba files appeal — only 1 copy instead of 2' },
    'tl-21-date': { pl: '05.2025', en: 'May 2025' },
    'tl-21': { pl: 'Zięba wypowiada pełnomocnictwo', en: 'Zięba terminates power of attorney' },
    'tl-22-date': { pl: '12.06.2025', en: 'Jun 12, 2025' },
    'tl-22': { pl: 'Apelacja adw. Klisia (NCN) — żądanie skazania', en: 'Appeal by NCN lawyer Kliś — demands conviction' },
    'tl-23-date': { pl: '28.01.2026', en: 'Jan 28, 2026' },
    'tl-23': { pl: 'Grzywna 5000 PLN z groźbą aresztu', en: '5,000 PLN fine with threat of arrest' },
    'tl-24-date': { pl: '02.2026', en: 'Feb 2026' },
    'tl-24': { pl: 'Złożenie skargi do ORA na Ziębę', en: 'Disciplinary complaint to Bar Council against Zięba' },
    'tl-25-date': { pl: '02.2026', en: 'Feb 2026' },
    'tl-25': { pl: 'Zgłoszenie szkody do ERGO Hestia', en: 'Insurance claim to ERGO Hestia' },
    'tl-26-date': { pl: '02.2026', en: 'Feb 2026' },
    'tl-26': { pl: 'Zawiadomienie do CBA (19 plików dowodowych)', en: 'Report to CBA (19 evidence files)' },

    // Footer
    'footer-disclaimer': {
      pl: 'Wszystkie informacje przedstawione na tej stronie opierają się na dokumentach sądowych, aktach prokuratorskich, nagraniach audio i korespondencji mailowej. Autor działał jako sygnalista w interesie publicznym, ujawniając nieprawidłowości w instytucji finansowanej z pieniędzy polskich podatników. Ochrona sygnalistów jest gwarantowana ustawą z dnia 14 czerwca 2024 r. o ochronie sygnalistów oraz Dyrektywą Parlamentu Europejskiego i Rady (UE) 2019/1937.',
      en: 'All information presented on this website is based on court documents, prosecution files, audio recordings, and email correspondence. The author acted as a whistleblower in the public interest, exposing irregularities at an institution funded by Polish taxpayers\' money. Whistleblower protection is guaranteed by the Act of June 14, 2024 on the Protection of Whistleblowers and Directive (EU) 2019/1937 of the European Parliament and of the Council.'
    }
  };

  // ============================================
  // ROUTE DEFINITIONS
  // ============================================
  const routes = {
    pl: {
      '': 'home',
      'korupcja': 'corruption',
      'sprawy': 'cases',
      'chronologia': 'timeline'
    },
    en: {
      '': 'home',
      'corruption': 'corruption',
      'cases': 'cases',
      'timeline': 'timeline'
    }
  };

  const routePaths = {
    pl: { home: '#pl', corruption: '#pl/korupcja', cases: '#pl/sprawy', timeline: '#pl/chronologia' },
    en: { home: '#en', corruption: '#en/corruption', cases: '#en/cases', timeline: '#en/timeline' }
  };

  // ============================================
  // STATE
  // ============================================
  let currentLang = 'pl';
  let currentPage = 'home';
  let theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

  // ============================================
  // DOM REFS
  // ============================================
  const root = document.documentElement;
  const langToggle = document.getElementById('lang-toggle');
  const langLabel = document.getElementById('lang-label');
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const navToggle = document.getElementById('nav-toggle');
  const siteNav = document.getElementById('site-nav');
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.page-section');

  // ============================================
  // THEME TOGGLE
  // ============================================
  root.setAttribute('data-theme', theme);
  updateThemeIcon();

  themeToggle.addEventListener('click', function () {
    theme = theme === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', theme);
    updateThemeIcon();
  });

  function updateThemeIcon() {
    themeToggle.innerHTML = theme === 'dark'
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  // ============================================
  // MOBILE NAV TOGGLE
  // ============================================
  navToggle.addEventListener('click', function () {
    const isOpen = siteNav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
    // Change hamburger to X
    navToggle.innerHTML = isOpen
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
  });

  // Close nav when a link is clicked (mobile)
  navLinks.forEach(function (link) {
    link.addEventListener('click', function () {
      siteNav.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
    });
  });

  // ============================================
  // LANGUAGE SWITCHING
  // ============================================
  langToggle.addEventListener('click', function () {
    var newLang = currentLang === 'pl' ? 'en' : 'pl';
    // Navigate to same page in new language
    var newHash = routePaths[newLang][currentPage];
    window.location.hash = newHash;
  });

  function applyLanguage(lang) {
    currentLang = lang;
    root.setAttribute('lang', lang);

    // Update lang toggle button
    langLabel.textContent = lang === 'pl' ? 'EN' : 'PL';
    langToggle.setAttribute('aria-label', lang === 'pl' ? 'Switch language to English' : 'Przełącz język na polski');

    // Update all translatable elements
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (translations[key] && translations[key][lang]) {
        // Check if content contains HTML
        if (translations[key][lang].indexOf('<') !== -1) {
          el.innerHTML = translations[key][lang];
        } else {
          el.textContent = translations[key][lang];
        }
      }
    });

    // Update nav links hrefs
    navLinks.forEach(function (link) {
      var route = link.getAttribute('data-route');
      if (route && routePaths[lang][route]) {
        link.setAttribute('href', routePaths[lang][route]);
      }
    });
  }

  // ============================================
  // ROUTING
  // ============================================
  function parseHash() {
    var hash = window.location.hash.replace('#', '') || 'pl';
    var parts = hash.split('/');
    var lang = (parts[0] === 'en') ? 'en' : 'pl';
    var pagePath = parts.slice(1).join('/') || '';
    var page = routes[lang][pagePath] || 'home';
    return { lang: lang, page: page };
  }

  function showPage(page) {
    currentPage = page;
    sections.forEach(function (s) { s.classList.remove('active'); });
    var target = document.getElementById('section-' + page);
    if (target) {
      target.classList.add('active');
    }
    // Update active nav
    navLinks.forEach(function (link) {
      link.classList.toggle('active', link.getAttribute('data-route') === page);
    });
    // Scroll to top
    window.scrollTo(0, 0);
  }

  function handleRoute() {
    var parsed = parseHash();
    applyLanguage(parsed.lang);
    showPage(parsed.page);
  }

  window.addEventListener('hashchange', handleRoute);

  // Initial route
  if (!window.location.hash) {
    window.location.hash = '#pl';
  } else {
    handleRoute();
  }

})();
