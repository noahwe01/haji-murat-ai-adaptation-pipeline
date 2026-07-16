# Neues Projekt aufsetzen — Checkliste

## 1. Projektordner erstellen
```
projekte/novel-to-screenplay_[TITEL]/
├── story.txt                  ← Quellroman hier ablegen
├── config/projekt.yaml        ← Genre, Ton, Referenzfilme
├── obsidian-vault/            ← Projekt-Vault (aus Template)
│   ├── START.md
│   ├── characters/REGISTER.md
│   ├── locations/REGISTER.md
│   ├── timeline/TIMELINE.md
│   ├── themes/THEMEN.md
│   ├── scenes/SZENEN.md
│   ├── config/projekt-konfiguration.md
│   ├── continuity_log/LOG.md
│   └── _templates/
├── output/
└── state/story_state.json
```

## 2. Obsidian-Vault registrieren
- Vault in Obsidian öffnen: "Open another vault" → "Open folder as vault"
- Vault-Pfad in `adaptions-brain/START.md` eintragen

## 3. Projekt konfigurieren
- `config/projekt.yaml` ausfüllen: Titel, Genre, Ton, Referenzfilme, Output-Format
- `obsidian-vault/config/projekt-konfiguration.md` synchron halten

## 4. Story laden
- `story.txt` im Projektordner ablegen
- Story Analyst starten
