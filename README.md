## ✅ Projektübersicht (professionell)

### Projektname
`DnD-Spellcards-Generator`

### Kurzbeschreibung
Ein Python-basiertes Tool, das eine strukturierte JSON-Zauberliste (Spells.json) in eine LaTeX-Karteikartenvorlage (cards.tex) konvertiert, um stilisierte D&D-5e-Zauberkarten zu erstellen.

### Zweck
- Automatisierte Generierung von druckfertigen Zauberkarten
- Konsistente Kartendesigns mit Farbschema je Magieschule
- Pflege und Erweiterung von Zaubertexten in einem leicht editierbaren Datenformat

---

## 🔧 Was das Tool macht

1. Liest spells.json (Zauberdaten)
2. Erzeugt LaTeX-Karten je Zauber mit:
   - Name
   - Grad
   - Schule
   - Wirkzeit
   - Reichweite
   - Rettungswurf
   - Wirkungsdauer
   - Komponenten
   - Beschreibung
   - Höhere Grade
3. Schreibt die gesammelte LaTeX-Ausgabe nach cards.tex

---

## 🧩 Dateistruktur

- generateCards.py – Generierungs-Skript
- Spells.json – Datenquelle
- cards.tex – Ziel-Ausgabe (LaTeX)
- README.md – Projektdokumentation
- LICENSE – Lizenz

---

## 🎯 Vorteile

- Einfaches Hinzufügen/Ändern von Zauberdaten (JSON)
- Keine manuelle LaTeX-Formatierung jeder Karte
- Einheitlicher visueller Stil
- Ideal für Spielleiter, D&D-Gruppen, Druckvorbereitung

---

## 🚀 Nutzung

1. Spells.json bearbeiten/erweitern
2. `python generateCards.py` ausführen
3. cards.tex mit LaTeX (z.B. `pdflatex`) kompilieren
4. Kartensätze drucken

---

## 💡 Erweiterungsmöglichkeiten

- Mehr Zauberschulen + Farben
- Karten pro Seite anpassbar (z.B. 2x2 / 3x2)
- Support für mehrsprachige Felder (EN/DE)
- Icon-/Symbolerweiterungen für Komponenten/Rettungswurf
- GUI / Web-Frontend für bequeme Eingabe

---

> Dieses Projekt ist ein schlankes, wartbares Toolkit für D&D-Spielleiter, die professionell aussehende Zauberkarten aus standardisierten Daten generieren wollen.P