---
title: Hadji Murat — Transliterations-Standard
tags: [context, transliteration, naming, consistency, hm]
created: 2026-04-23
status: canonical (pre-HM-Run)
---

# Transliterations-Standard

**Ein kanonischer Name pro Entität, Punkt.** Variants existieren im Roman (Tolstoi selbst wechselt gelegentlich zwischen "Hadji Murad" und "Hadji Murat"; Maude-Übersetzung hat ihre eigenen Präferenzen; historische Literatur verwendet wieder andere Formen). Für die Pipeline gilt: **was hier steht, ist kanonisch.** Jede Abweichung im Output-Text ist ein Qualitätsfehler, den Style Validator flaggt.

## Kern-Prinzip

Pipeline-Output ist **Englisch** (Treatment, Screenplay, State). Deshalb wird die **englische Maude-Translation** als Basis genommen — sie ist die verbreiteste englische Ausgabe und entspricht Tolstois eigenem Bekenntnis zum Übersetzer Aylmer Maude. Ausnahme: wo Maude inkonsistent ist, wählen wir die häufigste oder eindeutigste Form.

## Namensschlüssel (kanonisch)

### Protagonist
| Kanonisch | Varianten (nicht verwenden) | Quelle |
|-----------|----------------------------|--------|
| **Hadji Murad** | Hadji Murat, Haji Murad, Hajji Murad, Gadzhimurad, Xadji Murad, Xaji Murat | Maude (Tolstoi), Wikipedia historisch |

**Diskussions-Hinweis:** Tolstoi-Originaltitel hat in Russisch "Хаджи-Мурат" (mit -t). Maude wählt "Hadji Murad" (mit -d). **Für Pipeline: Hadji Murad**, weil es der englische Standard ist und auch im Romantext der Maude-Version dominiert. Konsequent durchziehen.

### Russische Hauptfiguren
| Kanonisch | Varianten | Hinweis |
|-----------|-----------|---------|
| **Michael Vorontsov** | Mikhail Vorontsov, Michail Woronzow | HMs Viceroy, "alter Vorontsov" |
| **Simon Vorontsov** | Semyon Vorontsov, Semen | Sohn des Viceroy, **explizit separat halten** |
| **Marya Vasilevna** | Maria Vasilyevna | Frau von Michael Vorontsov |
| **Nicholas I** | Nikolaus I, Nikolai Pavlovich | Zar (niemals "Nikolaus I." mit Punkt im englischen Output) |
| **Chernyshov** | Tschernyschow, Chernyshev | Kriegsminister |
| **Prince Baryatinsky** | Barjatinski, Baryatinskii | Neuer Flankenkommandant |
| **Loris-Melikov** | Loris Melikov (ohne Bindestrich NICHT) | Aide-de-camp, Armenier |
| **Prince Tarkhanov** | Tarkanov, Tarchanow | Dolmetscher in Tiflis |
| **Prince Vasili Dolgoruky** | Wassili Dolgoruki | Stellv. Kriegsminister |
| **Klugenau** | Klügenau | Russischer General, Flashback |
| **Meller-Zakomelsky** | Meller-Zakomelskii | Vozdvizhensk-General |
| **Poltoratsky** | Poltoratski | Garde-Offizier |
| **Major Petrov** | — | Fort-Kommandant |
| **Butler** | — | Junger Offizier (englischer Nachname, nicht übersetzen) |
| **Marya Dmitrievna** | Maria Dmitriewna | Petrovs Lebensgefährtin |
| **Avdeev** (Peter) | Avdeyev, Awdejew | Russischer Soldat |
| **Karganov** | Karganoff | Bezirks-Kommandant bei HMs Tod |

### Kaukasische Hauptfiguren
| Kanonisch | Varianten | Hinweis |
|-----------|-----------|---------|
| **Shamil** | Schamil, Chamil, Shamyl | Imam |
| **Hamzad** | Hamzat Bek, Gamzat-Bek | 2. Imam (Flashback) |
| **Akhmet Khan** | Ahmed Khan | Verstorbener Rivale (Flashback) |
| **Hadji Aga** | Haji Aga, Gadzhi Aga | Ehem. Kunak, Killer Kap. 25 |
| **Sado** | — | Kunak in Makhmet |
| **Bata** | — | Chechen-Guide |
| **Eldar** | — | Lesghier, HMs Murid |
| **Khanefi** | Chanefi | Avar, HMs Murid |
| **Gamzalo** | Gamsalo | Einäugiger Murid |
| **Khan Mahoma** | Khan Magoma, Chan Mahoma | Envoy-Murid |
| **Yusuf** | Jussuf, Yousef | HMs Sohn, 18 Jahre |
| **Patimat** | Fatimat | HMs Mutter |
| **Sofiat** | Sofia, Safiyat | HMs (junge) Ehefrau |
| **Abu Nutsal Khan** | Abu Nuzal | Avar-Khan, Flashback |
| **Umma Khan** | — | Avar-Khan, Flashback |
| **Jemal Eddin** | Dschemal Eddin, Jamaluddin | Shamils Schwiegervater |
| **Ibrahim Raschid** | Ibrahim Rashid | Shamils Officer, Hüter von HMs Familie |
| **Aminal** | — | Shamils Frau (jüngere) |
| **Zeidat** | Seidat | Shamils Frau (ältere) |
| **Bulach Khan** | Bulač | Jüngster Avar-Khan (Flashback) |

### Historische Referenz (nicht sprechend, aber erwähnt)
| Kanonisch | Hinweis |
|-----------|---------|
| **Yermolov** | Aleksei Yermolov, Ermolov — Kaukasus-General 1817-27 |
| **Velyaminov** | Ermolovs Nachfolger, Fortsetzer der Doktrin |
| **Ghazi Mollah** | Ghazi Muhammad, Kazi Mulla — 1. Imam |

**Hinweis zu Shamils Sohn:** Historisch "Ghazi Muhammad" (der Nachfolger, der HM ersetzt). Tolstoi erwähnt ihn indirekt. Falls in Adaption verwendet: **Ghazi Muhammad** (nicht mit 1. Imam verwechseln, der war Ghazi Mollah).

## Locations (kanonisch)

| Kanonisch | Varianten | Heutiger Name |
|-----------|-----------|---------------|
| **Tiflis** | Tbilisi, Tbilissi | Tbilisi, Georgien |
| **Vozdvizhensk** | Wozdwischensk, Kozdvižensk | (Ruinen, Tschetschenien) |
| **Nukha** | Nucha, Noukkha | Şəki, Aserbaidschan |
| **Vedeno** | Weden, Vedno | Wedeno, Tschetschenien |
| **Makhmet** | (fiktiver Aoul-Name bei Tolstoi) | — |
| **Khunzakh** | Chunzach | Chunsach, Dagestan |
| **Dargo** | — | (Dorf Tschetschenien) |
| **Mansokha Path** | (Tolstoi-spezifische Bezeichnung) | — |
| **Shalin Glade** | — | — |
| **St. Petersburg** | Sankt-Peterburg | — |
| **Kaukasus** | Caucasus (englisch), Kaukaz | Region |
| **Belarjik** | (Tolstoi-lokal) | nahe Nukha |

## Begriffe (kanonisch)

| Kanonisch | Alternativen | Bedeutung |
|-----------|--------------|-----------|
| **murid** | muridin (Plural arab.) | Sufi-gebundener Krieger. Pipeline: immer Singular + -s Plural ("murids"). Niemals kursiv nach erster Nennung. |
| **naib** | — | Stellvertreter-Gouverneur Shamils |
| **kunak** | — | Eides-gebundener Freund/Gast (Kaukasische Ehreninstitution) |
| **aoul** | aul, saulé | Bergdorf (kaukasisch) |
| **saklya** | sakla | Bergbewohner-Haus |
| **beshmet** | beschmet | Kaftan unter der cherkesska |
| **burka** | — | Filz-Umhang (nicht mit Burka-Verschleierung verwechseln) |
| **cherkesska** | circassian coat | Typische Männer-Tracht (Tschecherkess-Koat) |
| **papakha** | papakhi | Pelzmütze |
| **kinjal** | kindschal | Typischer Kaukasus-Dolch |
| **shashka** | schaschka | Säbel ohne Stichblatt |
| **taktikh** | — | historisch: Ausrüstung der Kosaken (optional) |
| **namaz** | Gebet | Muslimisches Pflicht-Gebet 5×/Tag |
| **Shariat** | Sharia | Islamisches Recht (Groß-S in historischem Kontext) |
| **Imam** | — | Religiös-politisches Oberhaupt |
| **Imamat** | Imamate | Shamils Staatsgebilde |
| **kizyak** | kiziak | Brennmaterial aus getrocknetem Dung |
| **dzhigit** | jighit, dschigit | Heldenhafter Reiter/Krieger |

## Schreibregeln

### Kyrillische Umlaute im Englischen Output
- **Umlaut-Ersatz nicht verwenden** (nicht "Woronzow", sondern "Vorontsov")
- **Keine deutschen Transliterationen** (Tolstois Pattern ist russisch → englisch, nicht russisch → deutsch)

### Apostrophe und Bindestriche
- **Bindestrich bei zusammengesetzten Namen:** Loris-Melikov, Meller-Zakomelsky, Hadji Murad (ohne Bindestrich aber fest-geschrieben)
- **Arabischer Partikel "Hadji":** kein Bindestrich nach Maude-Konvention ("Hadji Murad", nicht "Hadji-Murad" — außer in Tolstois russischem Titel "Хаджи-Мурат", der gebindestrichnet ist)

### Ränge und Titel
- **Prinz/Fürst** → immer **Prince** (vor dem Namen: "Prince Vorontsov")
- **Graf** → **Count** (kommt bei HM selten vor)
- **General** → als Rang, nicht als Name: "the general" klein, "General Klugenau" groß
- **Knjaz** (russ. Fürst-Titel) → immer **Prince** im Output

### Gebirgs-Bezirke
- **Dagestan** (nicht Daghestan, nicht Dagistan)
- **Tschetschenien** → im englischen Output **Chechnya**
- **Awarien** → **Avaria** (falls benötigt, selten)
- **Inguschetien** → **Ingushetia**

## Aliases-Liste (für Character Agent)

Für jede Figur müssen **alle Romantext-Varianten** als `aliases` im Voice Profile eingetragen werden, auch wenn nur die kanonische Form ausgegeben wird. Das ermöglicht dem Continuity Watcher, Inkonsistenzen im Zwischentext zu erkennen. Quelle: `graphify-out/characters.json` hat bereits aliases-Listen.

Beispiel:
```yaml
character:
  canonical: "Hadji Murad"
  aliases:
    - "Hadji Murad"
    - "Hadji Murat"
    - "Lieutenant Hadji Murad"
    - "Shamil's naib"
    - "the naib"
    - "the terrible mountain chief"
    - "murshid"
```

## Style-Validator-Regel

Style Validator prüft im Output:
1. Taucht eine Figur unter mehreren Schreibweisen auf? → Error
2. Werden Begriffe (murid, kunak, aoul) inkonsistent (groß/klein, kursiv/normal) verwendet? → Error
3. Wird "Prince" vor aristokratischen Namen verwendet (außer bei Zar)? → Warnung
4. Erscheinen deutsche oder kyrillische Hybridformen? → Error
5. Verwendet ein Kapitel "Hadji Murat" statt "Hadji Murad" (oder umgekehrt)? → Error

## Anwendungsregel

1. **Character Agent (Phase 2):** Konsumiert diese Liste, setzt `canonical` + `aliases` pro Voice Profile.
2. **World Agent (Phase 2):** Konsumiert die Locations-Liste.
3. **Adaptation Agent (Phase 5):** In jeder generierten Szene werden Figuren- und Ortsnamen **nur in kanonischer Form** geschrieben. Dialog-Sprache zwischen Figuren darf kulturspezifisch sein (HM mag Shamil "the red-bearded one" nennen — das ist legitime Figuren-Stimme, nicht Transliterations-Problem).
4. **Script Writer (Phase 6+9):** Final-Pass prüft Konsistenz gegen diese Liste.
5. **Style Validator (Phase 7.5):** Audit gegen diese Liste; Verstöße → Revision.
6. **User:** darf überschreiben, aber nur **einmal, durchgehend** — wenn "Mikhail Vorontsov" bevorzugt wird, gilt das für die ganze Adaption.

## Known Gaps / Open Questions

- **HMs Ehefrau Sofiat:** nicht in Maude-Text eindeutig. Eigene Wahl. Historisch attestierte Form könnte abweichen.
- **Nukha heute = Şəki** (Aserbaidschan) mit diakritischem Zeichen. Im englischen Skript: **Nukha** (zeitgenössische Bezeichnung zum Handlungsjahr).
- **Avar Transkriptionen** (z.B. Хlажи Мурад, HӀажи Мурад) sind in moderner Avar-Kyrillik andere Formen — für Film irrelevant, nur Theoriedokumentation.
- **Bata** und andere eher nur einnamige Figuren: Patronymik fehlt. Bei Tolstoi bewusst, nicht ergänzen.

## Wikilinks

- [[../../../adaptions-brain/konzepte/kaukasus-krieg-1851|kaukasus-krieg-1851]] — historischer Kontext
- [[../analysis/hm-figuren-bibel-raw|hm-figuren-bibel-raw]] — Voice Profiles
- [[../analysis/hm-plot-struktur|hm-plot-struktur]] — Szenen-Verankerung
- [[../../../adaptions-brain/autoren/tolstoi|tolstoi]] — Werk-Loyalität

## Quellen

- Maude-Übersetzung HM (Aylmer + Louise Maude, 1912) — Basis-Transliteration
- `graphify-out/characters.json` aliases-Felder (aus 5-Agent-Extraktion)
- Wikipedia: *Hadji Murad*, *Imam Shamil*, *Caucasian War*
- Eigenes [[../../../adaptions-brain/konzepte/kaukasus-krieg-1851]] für historische Namens-Fakten

---

#context #transliteration #naming #consistency #hm
