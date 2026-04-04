#!/usr/bin/env python3
"""
DnD 5e Spell Card Generator
============================
Reads a JSON file of spells and writes a cards.tex containing only
the \cardpage{...} blocks — ready to \input into your existing document.

Usage:
    python spellcards_generator.py spells.json
    python spellcards_generator.py spells.json -o cards.tex

JSON spell schema:
[
  {
    "name":        "Fireball",
    "school":      "hervorrufungsmagie",   // any \schoolname key you use
    "level":       3,                      // 0 = Zaubertrick
    "casting_time":"1 Aktion",
    "range":       "45 m",
    "components":  "V,G,M",
    "duration":    "Sofort",
    "material":    "Phosphor",             // omit or "" to leave empty
    "description": "Explosion mit 6 m Radius.\n8W6 Feuerschaden (RW halbiert).",
    "healing":     false,                  // true → adds \faHeart after name
    "page":        241                     // omit to skip \spellpage
  }
]
"""

import json
import sys
import argparse

CARDS_PER_PAGE = 8


def esc(text: str) -> str:
    """Escape special LaTeX characters in plain user text."""
    for old, new in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                     ("#", r"\#"), ("_", r"\_")]:
        text = text.replace(old, new)
    return text


def level_label(level: int) -> str:
    return "Zaubertrick" if level == 0 else f"Grad {level}"


def build_card(spell: dict) -> str:
    name       = esc(spell.get("name", "Unknown"))
    school     = spell.get("school", "hervorrufungsmagie")
    level      = int(spell.get("level", 0))
    healing    = spell.get("healing", False)
    page       = spell.get("page", None)
    cast_time  = esc(spell.get("casting_time", "1 Aktion"))
    rng        = esc(spell.get("range", "Selbst"))
    components = esc(spell.get("components", "V,G"))
    duration   = esc(spell.get("duration", "Sofort"))
    material   = esc(spell.get("material", ""))
    desc       = spell.get("description", "").replace("\n", r"\\")

    heart     = r" \faHeart" if healing else ""
    subtitle  = f"{level_label(level)} • \\schoolname{{{school}}}"
    page_line = f"\\vfill\\spellpage{{{page}}}" if page is not None else "\\vfill"

    return (
        f"\\begin{{spellcard}}\n"
        f"\\spellheader{{{name}{heart}}}{{{school}}}\n"
        f"  {{{subtitle}}}\n"
        f"\\vspace{{0.5mm}}\n"
        f"\\spellmeta{{{cast_time}}}{{{rng}}}{{{components}}}{{{duration}}}{{{material}}}\n"
        f"\\spelldesc{{{desc}}}\n"
        f"{page_line}\n"
        f"\\end{{spellcard}}"
    )


def build_tex(spells: list, include_backs: bool = True) -> str:
    cards = [build_card(s) for s in spells]

    while len(cards) % CARDS_PER_PAGE != 0:
        cards.append(r"\emptycard")

    pages = [cards[i:i + CARDS_PER_PAGE] for i in range(0, len(cards), CARDS_PER_PAGE)]
    lines = []

    for page_num, page_cards in enumerate(pages, 1):
        first = (page_num - 1) * CARDS_PER_PAGE + 1
        last  = page_num * CARDS_PER_PAGE
        lines.append(f"% {'=' * 60}")
        lines.append(f"% PAGE {page_num} — cards {first}–{last}")
        lines.append(f"% {'=' * 60}")
        lines.append(r"\cardpage")
        for i, card in enumerate(page_cards, 1):
            lines.append(f"{{% {first + i - 1}")
            lines.append(card + "%")
            lines.append("}")
        lines.append("")

    if include_backs:
        lines.append(f"% {'=' * 60}")
        lines.append("% BACK PAGES")
        lines.append(f"% {'=' * 60}")
        for page_num in range(1, len(pages) + 1):
            lines.append(f"% Back page {page_num}")
            lines.append(r"\cardpage")
            lines.append(r"{\cardback}{\cardback}{\cardback}{\cardback}")
            lines.append(r"{\cardback}{\cardback}{\cardback}{\cardback}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate \\cardpage blocks for your DnD spell card document."
    )
    parser.add_argument("input", help="JSON file with spell data")
    parser.add_argument("-o", "--output", default="cards.tex",
                        help="Output file (default: cards.tex)")
    parser.add_argument("--no-backs", action="store_true",
                        help="Omit card-back pages")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        spells = json.load(f)

    if not isinstance(spells, list):
        print("Error: JSON root must be an array.", file=sys.stderr)
        sys.exit(1)

    tex = build_tex(spells, include_backs=not args.no_backs)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(tex)

    print(f"✓ {len(spells)} spell(s) → {args.output}")


if __name__ == "__main__":
    main()
