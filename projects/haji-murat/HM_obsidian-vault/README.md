---
title: Hadji Murat — Obsidian Vault
status: pre-seeded (T4.3 abgeschlossen 2026-04-23)
---

# Hadji Murat — Obsidian Vault

Projekt-spezifisches **Second Brain** für die HM-Adaption. Pre-seeded 2026-04-23 (T4.3). Story Analyst + Character Agent + World Agent überschreiben diese Stubs in Phase 1–2.

**Status-Konvention:**
- `status: hypothesis` — Pre-Seed, darf überschrieben werden (mit Begründung)
- `status: extracted` — Agent-generiert aus Quelltext
- `status: canonical` — User-bestätigt, nicht mehr änderbar

## Vault-Struktur

| Ordner | Inhalt | Anzahl (Pre-Seed) |
|--------|--------|-------------------|
| [[analysis/]] | T2.3 HM-Werkanalyse (Plot, Figuren, Themen, Fusionen) | 4 Notes |
| [[characters/]] | Figuren-Stubs (Tier 1+2+Anker) | 36 |
| [[locations/]] | Top-15 Locations nach cinematic_weight | 15 |
| [[themes/]] | 5 Pflicht-Themen | 5 |
| [[timeline/]] | Historisch-dramaturgische Chronologie 1851–1852 | 1 |
| [[context/]] | Transliterations-Standard | 1 |
| [[brain-extensions/]] | Links ins globale `adaptions-brain/` | — |
| [[scenes/]] | (leer) — wird von Adaptation Agent Phase 5 befüllt | — |
| [[continuity_log/]] | (leer) — Runtime-Log | — |

## Einstiegspunkte

### Für Adaption-Planung
- **Werkgeist-These** → [[analysis/hm-themen-inventar]]
- **Akt-Struktur** → [[analysis/hm-plot-struktur]]
- **Figuren-Ranking** → [[analysis/hm-figuren-bibel-raw]]
- **Fusions-Entscheidungen** → [[analysis/hm-fusion-kandidaten]]

### Für einzelne Szenen-Arbeit
- **Welche Figur erscheint wann** → [[timeline/1851-1852]]
- **Welcher Ort** → [[locations/]] (alle 15 non-compressible Anker)
- **Was ist der thematische Gehalt** → [[themes/]] (5 Pflicht-Themen)

### Für Produktions-Entscheidungen
- **Transliteration kanonisch** → [[context/transliterations-standard]]
- **Historischer Kontext** → [[brain-extensions/kaukasus-krieg-1851]] (global)
- **Casting-Anker** → [[config/projekt.yaml]] im Projekt-Root

## Globale Brain-Verknüpfung

Das projekt-übergreifende Drehbuch-Gehirn (`adaptions-brain/`) ist **nicht** hier kopiert. Statt dessen sind die wichtigsten Notes als Wikilinks referenziert:

- [[../../../adaptions-brain/autoren/tolstoi|tolstoi]] — Autorenprofil
- [[../../../adaptions-brain/konzepte/tolstoi-erzaehlstil|tolstoi-erzaehlstil]] — Operationalisierung
- [[../../../adaptions-brain/konzepte/kaukasus-krieg-1851|kaukasus-krieg-1851]] — World-Anchor
- [[../../../adaptions-brain/theorie/adaptionstheorie-foundations|adaptionstheorie-foundations]]
- [[../../../adaptions-brain/patterns/figurenfusion|figurenfusion]]
- [[../../../adaptions-brain/patterns/plot-umstrukturierung|plot-umstrukturierung]]
- [[../../../adaptions-brain/patterns/kompression-roman|kompression-roman]]
- [[../../../adaptions-brain/patterns/antiheroische-fokalisierung|antiheroische-fokalisierung]]
- [[../../../adaptions-brain/techniken/framing-device|framing-device]]
- [[../../../adaptions-brain/techniken/intercutting-parallelhandlung|intercutting-parallelhandlung]]
- [[../../../adaptions-brain/konzepte/vier-figurenfunktionen|vier-figurenfunktionen]]
- [[../../../adaptions-brain/beispiele/english-patient-adaptation|english-patient-adaptation]] — HM-Primärvorbild
- [[../../../adaptions-brain/beispiele/barry-lyndon-thackeray|barry-lyndon-thackeray]] — VO-Disziplin

## Pre-Seed-Herkunft

Alle Stubs in diesem Vault wurden 2026-04-23 aus folgenden Quellen generiert:

1. **characters/** — aus `graphify-out/characters.json` (117 Knoten, 5-Agent-Extraktion) + Tier-1-Overrides für 10 Kernfiguren (physical_signature, casting_anchor, justification)
2. **locations/** — aus `graphify-out/locations.json` (133 Locations), Top-15 nach cinematic_weight
3. **timeline/1851-1852.md** — aus `graphify-out/PLOTLINES_REPORT.md` + `adaptions-brain/konzepte/kaukasus-krieg-1851.md` + Volltext-Kap. 1+25-Verifikation
4. **themes/** — aus `analysis/hm-themen-inventar.md` (5 Pflicht-Themen extrahiert)

## Vor dem Full-Run (Checkliste)

Vor dem vollständigen Lauf zu erledigen:
- [ ] Alle Stubs durchgehen: `status: hypothesis` vs. Story-Analyst-Phase-1-Output abgleichen
- [ ] **Simon Vorontsov vs. Michael Vorontsov** Trennung verifizieren (zwei separate Character-Stubs)
- [ ] HM-Familie vervollständigen (Sofiat, jüngere Kinder — nicht im Graphify erfasst)
- [ ] Fusion-Entscheidungen aus [[analysis/hm-fusion-kandidaten]] User-Freigabe
- [ ] Framework-Submodule auf aktuellen Super-Repo-Commit bumpen (sonst sieht Pipeline nicht die neuen Schema-Felder `physical_signature` + `justification` + `pacing_expected_variance`)

## Konventionen

- **Dateiname** = kebab-case-slug (ohne Umlaute, ohne Sonderzeichen)
- **YAML-Frontmatter** immer oben, mit `status:` + `tags:` + `source:`-Feldern
- **Wikilinks** bevorzugt relativ (`[[../analysis/hm-plot-struktur]]`) statt absolut
- **Deutsche Kommentare OK**, Output-Sprache gemäß Projektkonfiguration Englisch
- **Historische Anker** (historische reale Personen/Orte) niemals fusionieren (außer dokumentierte Ausnahmen siehe Fusion-Kandidaten)

---

*Vault-Root für `obsidian-vault/` des HM-Projekts.*
